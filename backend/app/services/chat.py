from datetime import datetime, timezone
from pathlib import Path
import re
from uuid import uuid4

from openai import AsyncOpenAI

from app.config import Settings
from app.models.schemas import AnswerMode, AnswerabilityResult, ChatRequest, ChatResponse, Citation
from app.services.answer_templates import match_answer_template, render_answer_template
from app.services.catalog import DocumentCatalog
from app.services.document_parser import DocumentParser
from app.services.feedback_store import ChatFeedbackStore
from app.services.retrieval_utils import deduplicate_hits, is_enumeration_query, prioritize_hits, retrieval_window, snippet_is_weak
from app.services.reranker import BGERerankerService
from app.services.vector_store import QdrantVectorStore, SearchHit


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
        hits = prioritize_hits(hits, request.question)[:effective_top_k]

        disclaimer = (
            "?듬?? ?щ떒 洹쒖젙, ?대? 吏移? 愿??踰뺣졊??諛뷀깢?쇰줈 ?앹꽦?⑸땲?? "
            "理쒖쥌 ?먮떒 ?꾩뿉??諛섎뱶???먮Ц怨?理쒖떊 媛쒖젙 ?щ?瑜??뺤씤?섏꽭??"
        )

        if not hits:
            return self._finalize_response(
                request=request,
                answer=(
                    "吏덈Ц怨?吏곸젒 ?곌껐?섎뒗 臾몄꽌瑜?李얠? 紐삵뻽?듬땲?? "
                    "臾몄꽌 踰붿쐞瑜?醫곹엳嫄곕굹 吏덈Ц??議곌툑 ??援ъ껜?곸쑝濡??묒꽦??二쇱꽭??"
                ),
                citations=[],
                confidence="low",
                disclaimer=disclaimer,
                retrieved_chunks=0,
                template_id=None,
                llm_used=False,
            )


        answerability = self._assess_answerability(request.question, hits)
        if not answerability.is_answerable:
            return self._finalize_response(
                request=request,
                answer='Insufficient evidence to answer reliably.',
                citations=[],
                confidence=answerability.confidence,
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
                "?꾩옱 LLM ?곌껐???ㅼ젙?섏? ?딆븘 寃?됰맂 臾몄꽌 ?붿빟留??쒓났?⑸땲??",
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
            page_label = f" / ?섏씠吏 {citation.page_number}" if citation.page_number else ""
            supplemental = self._supplemental_context(
                citation.document_id,
                citation.location,
                expand=is_list_query,
            )
            supplemental_contexts[citation.index] = supplemental
            supplemental_text = f"\n蹂닿컯 臾몃㎘:\n{supplemental}" if supplemental else ""
            context_blocks.append(
                f"[{citation.index}] ?쒕ぉ: {citation.title} / 遺꾨쪟: {citation.category.value} / ?꾩튂: {citation.location}{page_label}\n"
                f"?댁슜: {citation.snippet}{supplemental_text}"
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
                "?꾩옱 LLM ?곌껐???ㅼ젙?섏? ?딆븘 寃?됰맂 臾몄꽌 ?붿빟留??쒓났?⑸땲??",
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
                        f"吏덈Ц: {request.question}\n\n"
                        f"洹쇨굅 臾몄꽌:\n{prompt}\n\n"
                        "?붽뎄?ы빆: 異붿젙?쇰줈 ?듯븯吏 留먭퀬 洹쇨굅 ?녿뒗 ?⑥젙? 湲덉??쒕떎. "
                        "?몄슜? 諛섎뱶??[踰덊샇] ?뺤떇?쇰줈 ?쒓린?쒕떎."
                    ),
                },
            ],
        )

        message = completion.choices[0].message.content or "?듬????앹꽦?섏? 紐삵뻽?듬땲??"
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
                "?ㅻТ 吏?먰삎?쇰줈 媛꾧껐?섍퀬 ?뺥솗?섍쾶 ?듯븯?? ?듭떖 寃곕줎??癒쇱? ?쒖떆?섍퀬, "
                "諛붾줈 ?댁뼱??洹쇨굅? 二쇱쓽?ы빆??遺숈뿬??"
            ),
            AnswerMode.HR_ADMIN: (
                "?몄궗?대떦?먯쿂???듯븯?? 痍⑥뾽洹쒖튃, 蹂듬Т, ?뱀쭊, ?됯?, ?닿?, 吏뺢퀎, ?뱀씤 ?덉감? "
                "?덉쇅 議곌굔??援щ텇???ㅻ챸?섍퀬, ?ㅼ젣 泥섎━ ?쒖꽌瑜??④퍡 ?쒖떆?섎씪."
            ),
            AnswerMode.CONTRACT_REVIEW: (
                "怨꾩빟 寃???대떦?먯쿂???듯븯?? ?곸슜 議고빆, 梨낆엫 踰붿쐞, ?덉쇅, ?꾨씫 ?꾪뿕, "
                "遺꾩웳 ?뚯?瑜??섎닠 ?ㅻ챸?섍퀬, ?뺤씤???꾩슂??臾멸뎄瑜?吏싳뼱??"
            ),
            AnswerMode.PROJECT_MANAGEMENT: (
                "?ъ뾽愿由??대떦?먯쿂???듯븯?? ?ъ뾽 ?섑뻾 ?덉감, 吏묓뻾 湲곗?, 蹂닿퀬 ?먮쫫, "
                "?쇱젙 諛??곗텧臾?愿?먯뿉??鍮좎쭚?놁씠 援ъ“?뷀빐 ?ㅻ챸?섎씪."
            ),
            AnswerMode.PROCUREMENT_BID: (
                "援щℓ/?낆같 ?대떦?먯쿂???듯븯?? 援щℓ 諛⑹떇, 鍮꾧탳寃ъ쟻 ?먮뒗 ?낆같 ?꾩슂 ?щ?, "
                "寃?섏? 怨꾩빟 泥닿껐 ?ъ씤?? 利앸튃 臾몄꽌瑜?以묒떖?쇰줈 ?뺣━?섎씪."
            ),
            AnswerMode.AUDIT_RESPONSE: (
                "媛먯궗 ????대떦?먯쿂???듯븯?? ?덉감 ?꾨씫, 洹쒖젙 ?꾨컲 媛?μ꽦, 利앸튃 怨듬갚, "
                "?ы썑 蹂댁셿 ?꾩슂?ы빆???곗꽑?쒖쐞?濡??먭??섎씪."
            ),
        }[answer_mode]

        enumeration_instruction = (
            "吏덈Ц??紐⑸줉, 湲곗??? 吏곴툒蹂??먮뒗 ?좏삎蹂??뺣━瑜??붽뎄?섎㈃ ????ぉ留??듯븯吏 留먭퀬 "
            "洹쇨굅 臾몄꽌 ?덉뿉 ?덈뒗 愿????ぉ??媛?ν븳 踰붿쐞源뚯? 紐⑤몢 紐⑥븘 ?쒕굹 紐⑸줉 ?뺥깭濡??뺣━?섎씪. "
            "?쇰?留??뺤씤?섎㈃ ?꾨씫 媛?μ꽦??紐낆떆?섍퀬, ?뺤씤????ぉ怨?誘명솗????ぉ??援щ텇?섎씪."
            if is_enumeration_query
            else "吏덈Ц怨?吏곸젒 ?곌껐?섎뒗 湲곗?, ?곸슜 踰붿쐞, ?덉쇅瑜?癒쇱? ?쒖떆?섎씪."
        )

        return (
            "?뱀떊? ?뚯궗 ?대? 洹쒖젙怨?踰뺣졊??洹쇨굅濡??듬??섎뒗 ?낅Т ?곷떞 ?쒖뒪?쒖씠?? "
            "諛섎뱶???쒓났??洹쇨굅 臾몄꽌 踰붿쐞 ?덉뿉?쒕쭔 ?듯븯怨? 臾몄꽌???녿뒗 ?댁슜? 異붿젙?섏? 留덈씪. "
            "洹쇨굅媛 異⑸룎?섍굅??遺덈챸?뺥븯硫?洹??ъ떎??癒쇱? 紐낆떆?섎씪. "
            "?듬?? 癒쇱? 寃곕줎, ?ㅼ쓬??洹쇨굅 ?붿빟, 留덉?留됱뿉 二쇱쓽?ы빆 ?먮뒗 異붽? ?뺤씤?ы빆 ?쒖꽌濡??뺣━?섎씪. "
            f"{mode_instruction} {enumeration_instruction}"
        )

    def _confidence(self, score: float) -> str:
        if score >= 0.82:
            return "high"
        if score >= 0.68:
            return "medium"
        return "low"

    def _assess_answerability(self, question: str, hits: list[SearchHit]) -> AnswerabilityResult:
        if not hits:
            return AnswerabilityResult(
                is_answerable=False,
                confidence="low",
                reason="no retrieved evidence",
                selected_parent_ids=[],
            )

        evidence_units = self._collapse_evidence_units(hits)
        ranked_hits = sorted(evidence_units, key=lambda hit: hit.score, reverse=True)
        top_hits = ranked_hits[:3]
        top_score = top_hits[0].score
        average_score = sum(hit.score for hit in top_hits) / len(top_hits)
        strong_hits = [hit for hit in top_hits if hit.score >= 0.68 and not snippet_is_weak(hit.snippet)]
        rich_hits = [hit for hit in top_hits if self._metadata_richness(hit) >= 3]
        weak_hits = [hit for hit in top_hits if snippet_is_weak(hit.snippet)]
        selected_parent_ids = self._selected_parent_ids(ranked_hits)

        if (
            top_score < 0.55
            or average_score < 0.5
            or (len(top_hits) == 1 and not strong_hits)
            or (weak_hits and not rich_hits and average_score < 0.7)
        ):
            return AnswerabilityResult(
                is_answerable=False,
                confidence="low",
                reason="retrieved evidence is too weak to answer confidently",
                selected_parent_ids=selected_parent_ids,
            )

        confidence = "high" if top_score >= 0.82 and average_score >= 0.72 and len(strong_hits) >= 2 and rich_hits else "medium"
        reason = self._answerability_reason(top_hits, rich_hits, selected_parent_ids, confidence)
        return AnswerabilityResult(
            is_answerable=True,
            confidence=confidence,
            reason=reason,
            selected_parent_ids=selected_parent_ids,
        )

    def _collapse_evidence_units(self, hits: list[SearchHit]) -> list[SearchHit]:
        unique_hits: dict[str, SearchHit] = {}
        for hit in hits:
            key = hit.parent_id or f"{hit.document_id}:{hit.location}"
            current = unique_hits.get(key)
            if current is None or hit.score > current.score:
                unique_hits[key] = hit
        return list(unique_hits.values())

    def _selected_parent_ids(self, hits: list[SearchHit]) -> list[str]:
        parent_ids: list[str] = []
        seen: set[str] = set()
        for hit in hits:
            if hit.parent_id is None or hit.score < 0.6 or hit.parent_id in seen:
                continue
            seen.add(hit.parent_id)
            parent_ids.append(hit.parent_id)
            if len(parent_ids) >= 3:
                break
        return parent_ids

    def _metadata_richness(self, hit: SearchHit) -> int:
        fields = [
            hit.filename,
            hit.location,
            hit.path_key,
            hit.child_id,
            hit.parent_id,
            hit.source_type.value if hit.source_type is not None and hasattr(hit.source_type, "value") else hit.source_type,
        ]
        richness = sum(1 for field in fields if field not in (None, ""))
        if hit.page_number is not None:
            richness += 1
        if hit.is_addendum:
            richness += 1
        if hit.is_appendix:
            richness += 1
        return richness

    def _answerability_reason(
        self,
        hits: list[SearchHit],
        rich_hits: list[SearchHit],
        selected_parent_ids: list[str],
        confidence: str,
    ) -> str:
        top_score = hits[0].score if hits else 0.0
        richness = max((self._metadata_richness(hit) for hit in hits), default=0)
        selected_note = f"{len(selected_parent_ids)} parent groups" if selected_parent_ids else "no parent groups"
        return (
            f"top_score={top_score:.2f}; evidence_richness={richness}; "
            f"rich_hits={len(rich_hits)}; selected={selected_note}; confidence={confidence}"
        )

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

