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
from app.services.retrieval_utils import aggregate_parent_hits, deduplicate_hits, is_enumeration_query, prioritize_hits, retrieval_window, score_document_title_match, shortlist_documents_by_title, snippet_is_weak
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

        shortlisted_records = shortlist_documents_by_title(request.question, self.catalog.list_documents())
        shortlisted_ids = [record.id for record in shortlisted_records]

        hits = self.vector_store.search(
            question=request.question,
            categories=request.categories,
            top_k=candidate_count,
            document_ids=shortlisted_ids or None,
        )
        hits = deduplicate_hits(hits)
        hits = self.reranker.rerank(request.question, hits, top_k=effective_top_k)
        hits = deduplicate_hits(hits)
        parent_hits = aggregate_parent_hits(hits, request.question)
        hits = self._select_answer_hits(hits, parent_hits, request.question, effective_top_k)

        if shortlisted_records and self._needs_shortlist_fallback(hits, parent_hits):
            lexical_hits = self._search_shortlisted_document_sections(
                request.question,
                shortlisted_records,
                limit=candidate_count,
            )
            if lexical_hits:
                hits = deduplicate_hits(lexical_hits)
                parent_hits = aggregate_parent_hits(hits, request.question)
                hits = self._select_answer_hits(hits, parent_hits, request.question, effective_top_k)

        disclaimer = (
            "????? ????域뱀뮇?? ??? 筌왖燁? ?온??甕곕베議??獄쏅?源??곗쨮 ??밴쉐??몃빍?? "
            "筌ㅼ뮇伊??癒?뼊 ?袁⑸퓠??獄쏆꼶諭???癒???筌ㅼ뮇??揶쏆뮇????????類ㅼ뵥??뤾쉭??"
        )

        if not hits:
            return self._finalize_response(
                request=request,
                answer=(
                    "筌욌뜄揆??筌욊낯???怨뚭퍙??롫뮉 ?얜챷苑뚨몴?筌≪뼚? 筌륁궢六??щ빍?? "
                    "?얜챷苑?甕곕뗄?욅몴??リ낱?녑쳞怨뺢돌 筌욌뜄揆??鈺곌퀗?????닌딄퍥?怨몄몵嚥??臾믨쉐??雅뚯눘苑??"
                ),
                citations=[],
                confidence="low",
                disclaimer=disclaimer,
                retrieved_chunks=0,
                template_id=None,
                llm_used=False,
            )


        answerability = self._assess_answerability(request.question, hits, parent_hits)

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

        if not answerability.is_answerable:
            if citations:
                preview_lines = [
                    'Retrieved evidence is weak, so this is a document-grounded preview instead of a full answer.',
                    '',
                ]
                for citation in citations:
                    preview_lines.append(
                        f"[{citation.index}] {citation.title} / {citation.location}: {citation.snippet[:220]}"
                    )
                return self._finalize_response(
                    request=request,
                    answer="\n".join(preview_lines),
                    citations=citations,
                    confidence=answerability.confidence,
                    disclaimer=disclaimer,
                    retrieved_chunks=len(citations),
                    template_id=None,
                    llm_used=False,
                )

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


        template_id = match_answer_template(request.question, request.answer_mode)

        if self.client is None and template_id is None:
            preview_lines = [
                "?袁⑹삺 LLM ?怨뚭퍙????쇱젟??? ??녿툡 野꺜??곕쭆 ?얜챷苑??遺용튋筌???볥궗??몃빍??",
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
            page_label = f" / ??륁뵠筌왖 {citation.page_number}" if citation.page_number else ""
            supplemental = self._supplemental_context(
                citation.document_id,
                citation.location,
                expand=is_list_query,
            )
            supplemental_contexts[citation.index] = supplemental
            supplemental_text = f"\n癰귣떯而??얜챶??\n{supplemental}" if supplemental else ""
            context_blocks.append(
                f"[{citation.index}] ??뺛걠: {citation.title} / ?브쑬履? {citation.category.value} / ?袁⑺뒄: {citation.location}{page_label}\n"
                f"??곸뒠: {citation.snippet}{supplemental_text}"
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
                "?袁⑹삺 LLM ?怨뚭퍙????쇱젟??? ??녿툡 野꺜??곕쭆 ?얜챷苑??遺용튋筌???볥궗??몃빍??",
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
                        f"筌욌뜄揆: {request.question}\n\n"
                        f"域뱀눊援??얜챷苑?\n{prompt}\n\n"
                        "?遺쎈럡??鍮? ?곕뗄???곗쨮 ???릭筌왖 筌띾Þ??域뱀눊援???용뮉 ??μ젟?? 疫뀀뜆???뺣뼄. "
                        "?紐꾩뒠?? 獄쏆꼶諭??[甕곕뜇?? ?類ㅻ뻼??곗쨮 ??볥┛??뺣뼄."
                    ),
                },
            ],
        )

        message = completion.choices[0].message.content or "???????밴쉐??? 筌륁궢六??щ빍??"
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


    def _select_answer_hits(
        self,
        hits: list[SearchHit],
        parent_hits,
        question: str,
        top_k: int,
    ) -> list[SearchHit]:
        if not hits:
            return []

        selected_parent_ids = [
            parent_hit.parent_id
            for parent_hit in parent_hits
            if parent_hit.aggregate_score >= 0.55
        ][: max(top_k, 3)]

        if not selected_parent_ids:
            return prioritize_hits(hits, question)[:top_k]

        grouped: dict[str, list[SearchHit]] = {}
        for hit in hits:
            key = hit.parent_id or f"{hit.document_id}:{hit.location}"
            grouped.setdefault(key, []).append(hit)

        selected_hits: list[SearchHit] = []
        for parent_id in selected_parent_ids:
            group_hits = grouped.get(parent_id, [])
            if not group_hits:
                continue
            ranked_group = prioritize_hits(group_hits, question)
            selected_hits.append(ranked_group[0])

        if not selected_hits:
            return prioritize_hits(hits, question)[:top_k]

        return prioritize_hits(selected_hits, question)[:top_k]


    def _needs_shortlist_fallback(self, hits: list[SearchHit], parent_hits) -> bool:
        if not hits:
            return True
        if not parent_hits:
            return True
        top_parent = parent_hits[0]
        return top_parent.aggregate_score < 0.7 or top_parent.is_addendum or top_parent.is_appendix

    def _search_shortlisted_document_sections(
        self,
        question: str,
        records,
        *,
        limit: int,
    ) -> list[SearchHit]:
        tokens = self._tokenize(question)
        candidates: list[SearchHit] = []

        for record in records:
            structured_sections = []
            basic_sections = []
            try:
                if hasattr(self.parser, 'parse_structured_sections'):
                    structured_sections = self.parser.parse_structured_sections(Path(record.file_path))
            except Exception:
                structured_sections = []
            try:
                basic_sections = self.parser.parse(Path(record.file_path))
            except Exception:
                basic_sections = []

            raw_sections = structured_sections or basic_sections
            for index, section in enumerate(raw_sections):
                text = getattr(section, 'text', '')
                if not text:
                    continue
                location = getattr(section, 'location', f'Section {index + 1}')
                path_key = getattr(section, 'path_key', location)
                source_type = getattr(section, 'source_type', None)
                is_addendum = bool(getattr(section, 'is_addendum', False))
                is_appendix = bool(getattr(section, 'is_appendix', False))

                score = self._score_shortlisted_section(question, record.title, path_key, text, is_addendum, is_appendix)
                if score <= 0:
                    continue

                candidates.append(
                    SearchHit(
                        document_id=record.id,
                        title=record.title,
                        filename=record.filename,
                        category=record.category,
                        location=location,
                        page_number=getattr(section, 'page_number', None),
                        snippet=text[:240],
                        score=score,
                        chunk_index=index,
                        child_id=getattr(section, 'child_id', None),
                        parent_id=getattr(section, 'parent_id', None) or f"{record.id}::{path_key}",
                        path_key=path_key,
                        source_type=source_type,
                        is_addendum=is_addendum,
                        is_appendix=is_appendix,
                    )
                )

        ranked = sorted(
            candidates,
            key=lambda hit: (
                -hit.score,
                1 if snippet_is_weak(hit.snippet) else 0,
                hit.location,
            ),
        )
        return ranked[:limit]

    def _score_shortlisted_section(
        self,
        question: str,
        title: str,
        path_key: str,
        text: str,
        is_addendum: bool,
        is_appendix: bool,
    ) -> float:
        title_score = score_document_title_match(question, title)
        question_tokens = self._tokenize(question)
        body_tokens = self._tokenize(text)
        path_tokens = self._tokenize(path_key)
        body_overlap = len(question_tokens & body_tokens)
        path_overlap = len(question_tokens & path_tokens)
        score = title_score + (0.14 * body_overlap) + (0.09 * path_overlap)
        if is_addendum or is_appendix or snippet_is_weak(text):
            score -= 0.3
        return max(0.0, min(1.0, score))

    def _tokenize(self, value: str) -> set[str]:
        tokens: list[str] = []
        current: list[str] = []
        for char in value.lower():
            if char.isalnum():
                current.append(char)
                continue
            if len(current) >= 2:
                tokens.append(''.join(current))
            current = []
        if len(current) >= 2:
            tokens.append(''.join(current))
        return set(tokens)

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
                "??뿅?筌왖?癒곗굨??곗쨮 揶쏄쑨猿??랁??類μ넇??띿쓺 ???릭?? ???뼎 野껉퀡以???믪눘? ??뽯뻻??랁? "
                "獄쏅뗀以???곷선??域뱀눊援?? 雅뚯눘???鍮???븐늿肉??"
            ),
            AnswerMode.HR_ADMIN: (
                "?紐꾧텢????癒?퓗?????릭?? ?띯뫁毓썸뉩?뽱뒅, 癰귣벉龜, ?諭彛? ???, ???, 筌욌벚?? ?諭????됯컧?? "
                "??됱뇚 鈺곌퀗援???닌됲뀋????살구??랁? ??쇱젫 筌ｌ꼶????뽮퐣????ｍ뜞 ??뽯뻻??롮뵬."
            ),
            AnswerMode.CONTRACT_REVIEW: (
                "?④쑴鍮?野꺜??????癒?퓗?????릭?? ?怨몄뒠 鈺곌퀬鍮? 筌?굞??甕곕뗄?? ??됱뇚, ?袁⑥뵭 ?袁る퓮, "
                "?브쑴?????????롫떊 ??살구??랁? ?類ㅼ뵥???袁⑹뒄???얜㈇?꾤몴?筌욎떝堉??"
            ),
            AnswerMode.PROJECT_MANAGEMENT: (
                "??毓썸꽴???????癒?퓗?????릭?? ??毓???묐뻬 ??됯컧, 筌욌쵑六?疫꿸퀣?, 癰귣떯???癒?カ, "
                "??깆젟 獄??怨쀭뀱???온?癒?퓠????쥙彛??곸뵠 ?닌듼?酉鍮???살구??롮뵬."
            ),
            AnswerMode.PROCUREMENT_BID: (
                "?닌됤꼻/??녾컳 ????癒?퓗?????릭?? ?닌됤꼻 獄쎻뫗?? ??쑨?녑칰????癒?뮉 ??녾컳 ?袁⑹뒄 ???, "
                "野꺜??? ?④쑴鍮?筌ｋ떯猿?????? 筌앹빖???얜챷苑뚨몴?餓λ쵐???곗쨮 ?類ｂ봺??롮뵬."
            ),
            AnswerMode.AUDIT_RESPONSE: (
                "揶쏅Ŋ沅?????????癒?퓗?????릭?? ??됯컧 ?袁⑥뵭, 域뱀뮇???袁⑥뺘 揶쎛?關苑? 筌앹빖???⑤벉媛? "
                "????癰귣똻???袁⑹뒄??鍮???怨쀪퐨??뽰맄??嚥??癒???롮뵬."
            ),
        }[answer_mode]

        enumeration_instruction = (
            "筌욌뜄揆??筌뤴뫖以? 疫꿸퀣??? 筌욊낫?믦퉪??癒?뮉 ?醫륁굨癰??類ｂ봺???遺쎈럡??롢늺 ?????됵쭕????릭筌왖 筌띾Þ??"
            "域뱀눊援??얜챷苑???됰퓠 ??덈뮉 ?온???????揶쎛?館釉?甕곕뗄?욄틦?? 筌뤴뫀紐?筌뤴뫁釉???뺢돌 筌뤴뫖以??類κ묶嚥??類ｂ봺??롮뵬. "
            "???筌??類ㅼ뵥??롢늺 ?袁⑥뵭 揶쎛?關苑??筌뤿굞???랁? ?類ㅼ뵥?????됪?沃섎챸?????????닌됲뀋??롮뵬."
            if is_enumeration_query
            else "筌욌뜄揆??筌욊낯???怨뚭퍙??롫뮉 疫꿸퀣?, ?怨몄뒠 甕곕뗄?? ??됱뇚???믪눘? ??뽯뻻??롮뵬."
        )

        return (
            "?諭??? ???텢 ??? 域뱀뮇?숁?甕곕베議??域뱀눊援끾에??????롫뮉 ??끦??怨룸뼖 ??뽯뮞??뽰뵠?? "
            "獄쏆꼶諭????볥궗??域뱀눊援??얜챷苑?甕곕뗄????됰퓠??뺤춸 ???릭?? ?얜챷苑????용뮉 ??곸뒠?? ?곕뗄???? 筌띾뜄?? "
            "域뱀눊援끻첎? ?겸뫖猷??띻탢???븍뜄梨?類λ릭筌?域???????믪눘? 筌뤿굞???롮뵬. "
            "????? ?믪눘? 野껉퀡以? ??쇱벉??域뱀눊援??遺용튋, 筌띾뜆?筌띾맩肉?雅뚯눘???鍮??癒?뮉 ?곕떽? ?類ㅼ뵥??鍮???뽮퐣嚥??類ｂ봺??롮뵬. "
            f"{mode_instruction} {enumeration_instruction}"
        )

    def _confidence(self, score: float) -> str:
        if score >= 0.82:
            return "high"
        if score >= 0.68:
            return "medium"
        return "low"

    def _assess_answerability(
        self,
        question: str,
        hits: list[SearchHit],
        parent_hits=None,
    ) -> AnswerabilityResult:
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
        aggregated_hits = parent_hits if parent_hits is not None else aggregate_parent_hits(hits, question)
        selected_parent_ids = self._selected_parent_ids(aggregated_hits)
        top_parent = aggregated_hits[0] if aggregated_hits else None

        if top_parent is not None and top_parent.aggregate_score >= 0.62 and not top_parent.is_addendum and not top_parent.is_appendix:
            confidence = "high" if top_parent.aggregate_score >= 0.82 and top_parent.child_hit_count >= 2 else "medium"
            reason = (
                f"parent_score={top_parent.aggregate_score:.2f}; "
                f"child_hits={top_parent.child_hit_count}; "
                f"selected={len(selected_parent_ids)}; confidence={confidence}"
            )
            return AnswerabilityResult(
                is_answerable=True,
                confidence=confidence,
                reason=reason,
                selected_parent_ids=selected_parent_ids,
            )

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

    def _selected_parent_ids(self, parent_hits) -> list[str]:
        parent_ids: list[str] = []
        seen: set[str] = set()
        for hit in parent_hits:
            parent_id = getattr(hit, 'parent_id', None)
            aggregate_score = getattr(hit, 'aggregate_score', 0.0)
            if parent_id is None or aggregate_score < 0.5 or parent_id in seen:
                continue
            seen.add(parent_id)
            parent_ids.append(parent_id)
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




