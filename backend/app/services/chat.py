from datetime import datetime, timezone
from pathlib import Path
import re
from uuid import uuid4

from openai import AsyncOpenAI

from app.config import Settings
from app.models.schemas import AnswerMode, ChatRequest, ChatResponse, Citation
from app.services.answer_templates import match_answer_template, render_answer_template
from app.services.catalog import DocumentCatalog
from app.services.document_parser import DocumentParser
from app.services.feedback_store import ChatFeedbackStore
from app.services.retrieval_utils import deduplicate_hits, is_enumeration_query, retrieval_window
from app.services.reranker import BGERerankerService
from app.services.vector_store import QdrantVectorStore


class ChatService:
    def __init__(
        self,
        settings: Settings,
        vector_store: QdrantVectorStore,
        reranker: BGERerankerService,
        catalog: DocumentCatalog,
        parser: DocumentParser,
        feedback_store: ChatFeedbackStore,
    ) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.reranker = reranker
        self.catalog = catalog
        self.parser = parser
        self.feedback_store = feedback_store
        self.client = (
            AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
            if settings.openai_api_key
            else None
        )

    async def answer(self, request: ChatRequest) -> ChatResponse:
        is_list_query = is_enumeration_query(request.question)
        top_k = request.top_k or self.settings.top_k
        effective_top_k, candidate_count = retrieval_window(
            request.question,
            top_k=top_k,
            rerank_candidates=self.settings.rerank_candidates,
        )

        hits = self.vector_store.search(
            question=request.question,
            categories=request.categories,
            top_k=candidate_count,
        )
        hits = deduplicate_hits(hits)
        hits = self.reranker.rerank(request.question, hits, top_k=effective_top_k)
        hits = deduplicate_hits(hits)

        disclaimer = (
            "답변은 사단 규정, 내부 지침, 관련 법령을 바탕으로 생성됩니다. "
            "최종 판단 전에는 반드시 원문과 최신 개정 여부를 확인하세요."
        )

        if not hits:
            return self._finalize_response(
                request=request,
                answer=(
                    "질문과 직접 연결되는 문서를 찾지 못했습니다. "
                    "문서 범위를 좁히거나 질문을 조금 더 구체적으로 작성해 주세요."
                ),
                citations=[],
                confidence="low",
                disclaimer=disclaimer,
                retrieved_chunks=0,
                template_id=None,
                llm_used=False,
            )

        citations = [
            Citation(
                index=index,
                document_id=hit.document_id,
                title=hit.title,
                filename=hit.filename,
                category=hit.category,
                location=hit.location,
                page_number=hit.page_number,
                snippet=hit.snippet,
                score=round(hit.score, 4),
            )
            for index, hit in enumerate(hits, start=1)
        ]

        template_id = match_answer_template(request.question, request.answer_mode)

        if self.client is None and template_id is None:
            preview_lines = [
                "현재 LLM 연결이 설정되지 않아 검색된 문서 요약만 제공합니다.",
                "",
            ]
            for citation in citations:
                preview_lines.append(
                    f"[{citation.index}] {citation.title} / {citation.location}: {citation.snippet[:220]}"
                )
            return self._finalize_response(
                request=request,
                answer="\n".join(preview_lines),
                citations=citations,
                confidence=self._confidence(hits[0].score),
                disclaimer=disclaimer,
                retrieved_chunks=len(citations),
                template_id=template_id,
                llm_used=False,
            )

        supplemental_contexts: dict[int, str] = {}
        context_blocks = []
        for citation in citations:
            page_label = f" / 페이지 {citation.page_number}" if citation.page_number else ""
            supplemental = self._supplemental_context(
                citation.document_id,
                citation.location,
                expand=is_list_query,
            )
            supplemental_contexts[citation.index] = supplemental
            supplemental_text = f"\n보강 문맥:\n{supplemental}" if supplemental else ""
            context_blocks.append(
                f"[{citation.index}] 제목: {citation.title} / 분류: {citation.category.value} / 위치: {citation.location}{page_label}\n"
                f"내용: {citation.snippet}{supplemental_text}"
            )

        if template_id is not None:
            rendered_answer = render_answer_template(
                template_id,
                citations,
                supplemental_contexts=supplemental_contexts,
            )
            if rendered_answer is not None:
                return self._finalize_response(
                    request=request,
                    answer=rendered_answer,
                    citations=citations,
                    confidence=self._confidence(hits[0].score),
                    disclaimer=disclaimer,
                    retrieved_chunks=len(citations),
                    template_id=template_id,
                    llm_used=False,
                )

        if self.client is None:
            preview_lines = [
                "현재 LLM 연결이 설정되지 않아 검색된 문서 요약만 제공합니다.",
                "",
            ]
            for citation in citations:
                preview_lines.append(
                    f"[{citation.index}] {citation.title} / {citation.location}: {citation.snippet[:220]}"
                )
            return self._finalize_response(
                request=request,
                answer="\n".join(preview_lines),
                citations=citations,
                confidence=self._confidence(hits[0].score),
                disclaimer=disclaimer,
                retrieved_chunks=len(citations),
                template_id=template_id,
                llm_used=False,
            )

        prompt = "\n\n".join(context_blocks)

        completion = await self.client.chat.completions.create(
            model=self.settings.llm_model,
            temperature=0.1 if is_list_query else 0.2,
            messages=[
                {
                    "role": "system",
                    "content": self._system_prompt(request.answer_mode, is_list_query),
                },
                {
                    "role": "user",
                    "content": (
                        f"질문: {request.question}\n\n"
                        f"근거 문서:\n{prompt}\n\n"
                        "요구사항: 추정으로 답하지 말고 근거 없는 단정은 금지한다. "
                        "인용은 반드시 [번호] 형식으로 표기한다."
                    ),
                },
            ],
        )

        message = completion.choices[0].message.content or "답변을 생성하지 못했습니다."
        return self._finalize_response(
            request=request,
            answer=message.strip(),
            citations=citations,
            confidence=self._confidence(hits[0].score),
            disclaimer=disclaimer,
            retrieved_chunks=len(citations),
            template_id=template_id,
            llm_used=True,
        )

    def _finalize_response(
        self,
        *,
        request: ChatRequest,
        answer: str,
        citations: list[Citation],
        confidence: str,
        disclaimer: str,
        retrieved_chunks: int,
        template_id: str | None,
        llm_used: bool,
    ) -> ChatResponse:
        answer, citations = _prune_citations_to_answer(answer, citations)
        response = ChatResponse(
            response_id=uuid4().hex,
            generated_at=datetime.now(timezone.utc),
            answer=answer,
            citations=citations,
            confidence=confidence,
            disclaimer=disclaimer,
            retrieved_chunks=retrieved_chunks,
        )
        try:
            self.feedback_store.record_interaction(
                request=request,
                response=response,
                template_id=template_id,
                llm_used=llm_used,
            )
        except Exception:
            pass
        return response

    def _system_prompt(self, answer_mode: AnswerMode, is_enumeration_query: bool) -> str:
        mode_instruction = {
            AnswerMode.STANDARD: (
                "실무 지원형으로 간결하고 정확하게 답하라. 핵심 결론을 먼저 제시하고, "
                "바로 이어서 근거와 주의사항을 붙여라."
            ),
            AnswerMode.HR_ADMIN: (
                "인사담당자처럼 답하라. 취업규칙, 복무, 승진, 평가, 휴가, 징계, 승인 절차와 "
                "예외 조건을 구분해 설명하고, 실제 처리 순서를 함께 제시하라."
            ),
            AnswerMode.CONTRACT_REVIEW: (
                "계약 검토 담당자처럼 답하라. 적용 조항, 책임 범위, 예외, 누락 위험, "
                "분쟁 소지를 나눠 설명하고, 확인이 필요한 문구를 짚어라."
            ),
            AnswerMode.PROJECT_MANAGEMENT: (
                "사업관리 담당자처럼 답하라. 사업 수행 절차, 집행 기준, 보고 흐름, "
                "일정 및 산출물 관점에서 빠짐없이 구조화해 설명하라."
            ),
            AnswerMode.PROCUREMENT_BID: (
                "구매/입찰 담당자처럼 답하라. 구매 방식, 비교견적 또는 입찰 필요 여부, "
                "검수와 계약 체결 포인트, 증빙 문서를 중심으로 정리하라."
            ),
            AnswerMode.AUDIT_RESPONSE: (
                "감사 대응 담당자처럼 답하라. 절차 누락, 규정 위반 가능성, 증빙 공백, "
                "사후 보완 필요사항을 우선순위대로 점검하라."
            ),
        }[answer_mode]

        enumeration_instruction = (
            "질문이 목록, 기준표, 직급별 또는 유형별 정리를 요구하면 한 항목만 답하지 말고 "
            "근거 문서 안에 있는 관련 항목을 가능한 범위까지 모두 모아 표나 목록 형태로 정리하라. "
            "일부만 확인되면 누락 가능성을 명시하고, 확인된 항목과 미확인 항목을 구분하라."
            if is_enumeration_query
            else "질문과 직접 연결되는 기준, 적용 범위, 예외를 먼저 제시하라."
        )

        return (
            "당신은 회사 내부 규정과 법령을 근거로 답변하는 업무 상담 시스템이다. "
            "반드시 제공된 근거 문서 범위 안에서만 답하고, 문서에 없는 내용은 추정하지 마라. "
            "근거가 충돌하거나 불명확하면 그 사실을 먼저 명시하라. "
            "답변은 먼저 결론, 다음에 근거 요약, 마지막에 주의사항 또는 추가 확인사항 순서로 정리하라. "
            f"{mode_instruction} {enumeration_instruction}"
        )

    def _confidence(self, score: float) -> str:
        if score >= 0.82:
            return "high"
        if score >= 0.68:
            return "medium"
        return "low"

    def _supplemental_context(self, document_id: str, location: str, expand: bool) -> str:
        record = self.catalog.get_document(document_id)
        if record is None:
            return ""

        try:
            sections = self.parser.parse(Path(record.file_path))
        except Exception:
            return ""

        index = next((idx for idx, section in enumerate(sections) if section.location == location), None)
        if index is None:
            return ""

        window_before = 1
        window_after = 5 if expand else 2
        start = max(0, index - window_before)
        end = min(len(sections), index + window_after)
        return "\n\n".join(f"{section.location}: {section.text}" for section in sections[start:end])


def _prune_citations_to_answer(answer: str, citations: list[Citation]) -> tuple[str, list[Citation]]:
    referenced_indices = _extract_citation_indices(answer)
    if not referenced_indices:
        return answer, citations

    citations_by_index = {citation.index: citation for citation in citations}
    if any(index not in citations_by_index for index in referenced_indices):
        return answer, citations

    remap = {old_index: new_index for new_index, old_index in enumerate(referenced_indices, start=1)}
    pruned_citations = [
        citations_by_index[old_index].model_copy(update={"index": remap[old_index]})
        for old_index in referenced_indices
    ]

    def replace_reference(match: re.Match[str]) -> str:
        old_index = int(match.group(1))
        if old_index not in remap:
            return match.group(0)
        return f"[{remap[old_index]}]"

    normalized_answer = re.sub(r"\[(\d+)\]", replace_reference, answer)
    return normalized_answer, pruned_citations


def _extract_citation_indices(answer: str) -> list[int]:
    seen: set[int] = set()
    indices: list[int] = []
    for match in re.finditer(r"\[(\d+)\]", answer):
        index = int(match.group(1))
        if index in seen:
            continue
        seen.add(index)
        indices.append(index)
    return indices
