import asyncio

from app.config import Settings
from app.models.schemas import ChatRequest, Citation, DocumentCategory
from app.services.chat import ChatService, _extract_citation_indices, _prune_citations_to_answer
from app.services.vector_store import SearchHit


def make_citation(index: int) -> Citation:
    return Citation(
        index=index,
        document_id=f'doc-{index}',
        title=f'Doc {index}',
        filename=f'doc-{index}.md',
        category=DocumentCategory.RULE,
        location=f'Section {index}',
        page_number=None,
        snippet=f'Snippet {index}',
        score=0.9,
    )


def test_extract_citation_indices_preserves_first_appearance_order() -> None:
    answer = 'Answer [4][3] then [2][8] and [4] again'

    indices = _extract_citation_indices(answer)

    assert indices == [4, 3, 2, 8]


def test_prune_citations_to_answer_reorders_and_renumbers() -> None:
    citations = [make_citation(index) for index in range(1, 9)]
    answer = 'Answer [4][3]\nthen [2][8]\nagain [4]'

    normalized_answer, pruned_citations = _prune_citations_to_answer(answer, citations)

    assert normalized_answer == 'Answer [1][2]\nthen [3][4]\nagain [1]'
    assert [citation.index for citation in pruned_citations] == [1, 2, 3, 4]
    assert [citation.document_id for citation in pruned_citations] == ['doc-4', 'doc-3', 'doc-2', 'doc-8']


def test_prune_citations_to_answer_keeps_original_when_reference_is_missing() -> None:
    citations = [make_citation(index) for index in range(1, 4)]
    answer = 'Answer [2][5]'

    normalized_answer, pruned_citations = _prune_citations_to_answer(answer, citations)

    assert normalized_answer == answer
    assert pruned_citations == citations


def make_hit(*, document_id: str = 'doc-1', score: float = 0.41, parent_id: str | None = None, child_id: str | None = None) -> SearchHit:
    return SearchHit(
        document_id,
        'Policy Guide',
        'travel.md',
        DocumentCategory.RULE,
        'Chapter 3 > Section 10',
        3,
        'Appendix <2024-01-01>.',
        score,
        0,
        child_id=child_id,
        parent_id=parent_id,
        path_key='Chapter 3>Section 10>Clause 1',
        source_type=None,
        is_addendum=False,
        is_appendix=False,
    )


class FakeVectorStore:
    def __init__(self, hits: list[SearchHit]) -> None:
        self.hits = hits
        self.calls: list[tuple[str, list[DocumentCategory], int, list[str] | None]] = []

    def search(self, *, question: str, categories: list[DocumentCategory], top_k: int, document_ids=None) -> list[SearchHit]:
        self.calls.append((question, categories, top_k, document_ids))
        return list(self.hits)


class FakeReranker:
    def __init__(self, hits: list[SearchHit]) -> None:
        self.hits = hits
        self.calls: list[tuple[str, int]] = []

    def rerank(self, query: str, hits: list[SearchHit], top_k: int) -> list[SearchHit]:
        self.calls.append((query, top_k))
        return list(self.hits)


class BlockingCatalog:
    def list_documents(self):
        return []

    def get_document(self, document_id: str):
        raise AssertionError('catalog should not be consulted for weak evidence')


class BlockingParser:
    def parse(self, path):
        raise AssertionError('parser should not be consulted for weak evidence')


class RecordingFeedbackStore:
    def __init__(self) -> None:
        self.records: list[tuple[object, object, object, object]] = []

    def record_interaction(self, *, request, response, template_id, llm_used) -> None:
        self.records.append((request, response, template_id, llm_used))


def test_assess_answerability_rejects_weak_evidence_sets() -> None:
    service = ChatService(
        Settings(openai_api_key=''),
        FakeVectorStore([make_hit(score=0.42)]),
        FakeReranker([make_hit(score=0.42)]),
        BlockingCatalog(),
        BlockingParser(),
        RecordingFeedbackStore(),
    )

    result = service._assess_answerability('Where is the travel policy?', [make_hit(score=0.42)])

    assert result.is_answerable is False
    assert result.confidence == 'low'
    assert result.selected_parent_ids == []
    assert 'evidence' in result.reason.lower()


def test_assess_answerability_accepts_strong_parent_group() -> None:
    hit = SearchHit(
        'doc-1',
        '?? ??',
        'travel.md',
        DocumentCategory.RULE,
        '\uc81c10\uc870',
        3,
        '?10? ??? ?? ??? ??? ??.',
        0.58,
        0,
        child_id='child-1',
        parent_id='parent-1',
        path_key='?3?>?10?',
        source_type=None,
        is_addendum=False,
        is_appendix=False,
    )
    service = ChatService(
        Settings(openai_api_key=''),
        FakeVectorStore([hit]),
        FakeReranker([hit]),
        BlockingCatalog(),
        BlockingParser(),
        RecordingFeedbackStore(),
    )

    parent_hits = [
        type('ParentHit', (), {
            'parent_id': 'parent-1',
            'aggregate_score': 0.72,
            'child_hit_count': 1,
            'is_addendum': False,
            'is_appendix': False,
        })()
    ]

    result = service._assess_answerability('?? ??? ??? ?? ??? ????', [hit], parent_hits)

    assert result.is_answerable is True
    assert result.confidence == 'medium'
    assert result.selected_parent_ids == ['parent-1']


def test_answer_falls_back_without_generation_for_weak_evidence() -> None:
    weak_hit = make_hit(score=0.39)
    feedback_store = RecordingFeedbackStore()
    service = ChatService(
        Settings(openai_api_key=''),
        FakeVectorStore([weak_hit]),
        FakeReranker([weak_hit]),
        BlockingCatalog(),
        BlockingParser(),
        feedback_store,
    )

    response = asyncio.run(service.answer(ChatRequest(question='Where is the travel policy?')))

    assert response.answer.startswith('Retrieved evidence is weak')
    assert len(response.citations) == 1
    assert response.confidence == 'low'
    assert response.retrieved_chunks == 1
    assert len(feedback_store.records) == 1
    assert feedback_store.records[0][2] is None
    assert feedback_store.records[0][3] is False



def test_answer_uses_document_title_shortlist_when_question_names_document() -> None:
    from datetime import datetime, timezone
    from app.models.schemas import CategorySource, DocumentDomain, DocumentStatus, DocumentRecord

    hit = SearchHit(
        'doc-1',
        '취업규칙',
        'rules.md',
        DocumentCategory.RULE,
        '제10조',
        1,
        '제10조 징계 절차는 다음과 같다.',
        0.72,
        0,
        child_id='child-1',
        parent_id='parent-1',
        path_key='제10조',
        source_type=None,
        is_addendum=False,
        is_appendix=False,
    )
    now = datetime.now(timezone.utc)
    record = DocumentRecord(
        id='doc-1',
        title='취업규칙',
        filename='rules.md',
        stored_filename='rules.md',
        file_path='/tmp/rules.md',
        category=DocumentCategory.RULE,
        category_source=CategorySource.AUTO,
        domain=DocumentDomain.OTHER,
        tags=[],
        status=DocumentStatus.READY,
        uploaded_at=now,
        updated_at=now,
    )

    class ListingCatalog(BlockingCatalog):
        def list_documents(self):
            return [record]

    feedback_store = RecordingFeedbackStore()
    vector_store = FakeVectorStore([hit])
    service = ChatService(
        Settings(openai_api_key=''),
        vector_store,
        FakeReranker([hit]),
        ListingCatalog(),
        BlockingParser(),
        feedback_store,
    )

    response = asyncio.run(service.answer(ChatRequest(question='취업규칙에서 징계 절차를 단계별로 설명해줘')))

    assert vector_store.calls[0][3] == ['doc-1']
    assert response.citations





def test_answer_uses_shortlisted_document_sections_as_fallback() -> None:
    from datetime import datetime, timezone
    from app.models.schemas import CategorySource, DocumentDomain, DocumentStatus, DocumentRecord, StructuredSection, ChunkSourceType

    now = datetime.now(timezone.utc)
    record = DocumentRecord(
        id='doc-1',
        title='Employment Rules',
        filename='rules.md',
        stored_filename='rules.md',
        file_path='/tmp/rules.md',
        category=DocumentCategory.RULE,
        category_source=CategorySource.AUTO,
        domain=DocumentDomain.OTHER,
        tags=[],
        status=DocumentStatus.READY,
        uploaded_at=now,
        updated_at=now,
    )

    class ListingCatalog(BlockingCatalog):
        def list_documents(self):
            return [record]

    class StructuredParser(BlockingParser):
        def parse_structured_sections(self, path):
            return [
                StructuredSection(
                    source_type=ChunkSourceType.ARTICLE,
                    text='Section 10 disciplinary procedure requires prior notice, explanation opportunity, and committee review.',
                    chapter_label='Chapter 3',
                    section_label=None,
                    article_label='Section 10',
                    paragraph_label='Clause 1',
                    item_label=None,
                    effective_date=None,
                    path_key='Chapter 3>Section 10>Clause 1',
                    page_number=1,
                    location='Section 10 Clause 1',
                    is_addendum=False,
                    is_appendix=False,
                )
            ]

    feedback_store = RecordingFeedbackStore()
    vector_store = FakeVectorStore([])
    service = ChatService(
        Settings(openai_api_key=''),
        vector_store,
        FakeReranker([]),
        ListingCatalog(),
        StructuredParser(),
        feedback_store,
    )

    response = asyncio.run(service.answer(ChatRequest(question='Explain disciplinary procedure in Employment Rules step by step')))

    assert response.citations
    assert response.citations[0].document_id == 'doc-1'



def test_score_shortlisted_section_prefers_article_body_over_addendum() -> None:
    service = ChatService(
        Settings(openai_api_key=''),
        FakeVectorStore([]),
        FakeReranker([]),
        BlockingCatalog(),
        BlockingParser(),
        RecordingFeedbackStore(),
    )

    article_score = service._score_shortlisted_section(
        '\ucde8\uc5c5\uaddc\uce59\uc5d0\uc11c \uc9d5\uacc4 \uc808\ucc28\ub97c \ub2e8\uacc4\ubcc4\ub85c \uc124\uba85\ud574\uc918',
        '[3-18] \ucde8\uc5c5\uaddc\uce59(2026.1.1.)',
        '\uc81c10\uc870',
        '\uc81c10\uc870 \uc9d5\uacc4 \uc808\ucc28\ub294 \uc0ac\uc804 \ud1b5\uc9c0, \uc18c\uba85 \uae30\ud68c, \uc704\uc6d0\ud68c \uc2ec\uc758 \uc21c\uc73c\ub85c \uc9c4\ud589\ud55c\ub2e4.',
        'article',
        False,
        False,
    )
    addendum_score = service._score_shortlisted_section(
        '\ucde8\uc5c5\uaddc\uce59\uc5d0\uc11c \uc9d5\uacc4 \uc808\ucc28\ub97c \ub2e8\uacc4\ubcc4\ub85c \uc124\uba85\ud574\uc918',
        '[3-18] \ucde8\uc5c5\uaddc\uce59(2026.1.1.)',
        '\ubd80\uce59',
        '\ubd80\uce59 <2025.12.16.>',
        'addendum',
        True,
        False,
    )

    assert article_score > addendum_score


def test_tokenize_handles_korean_particles_for_shortlisted_sections() -> None:
    service = ChatService(
        Settings(openai_api_key=''),
        FakeVectorStore([]),
        FakeReranker([]),
        BlockingCatalog(),
        BlockingParser(),
        RecordingFeedbackStore(),
    )

    tokens = service._tokenize('\ucde8\uc5c5\uaddc\uce59\uc5d0\uc11c \uc9d5\uacc4 \uc808\ucc28\ub97c \ub2e8\uacc4\ubcc4\ub85c \uc124\uba85\ud574\uc918')

    assert '\ucde8\uc5c5\uaddc\uce59' in tokens
    assert '\uc808\ucc28' in tokens
