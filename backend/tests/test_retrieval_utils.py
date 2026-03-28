from app.models.schemas import DocumentCategory
from app.services.retrieval_utils import (
    aggregate_parent_hits,
    deduplicate_hits,
    is_enumeration_query,
    needs_targeted_expansion,
    needs_wide_candidate_search,
    needs_wide_top_k,
    prioritize_hits,
    retrieval_window,
    score_document_title_match,
    shortlist_documents_by_title,
    snippet_is_weak,
    title_matches_question,
)
from app.services.vector_store import SearchHit


def test_deduplicate_hits_keeps_first_unique_chunk() -> None:
    hits = [
        SearchHit('doc-1', '문서1', 'a.md', DocumentCategory.RULE, '구간 1', None, '첫번째', 0.9, 0),
        SearchHit('doc-1', '문서1', 'a.md', DocumentCategory.RULE, '구간 1', None, '중복', 0.8, 0),
        SearchHit('doc-1', '문서1', 'a.md', DocumentCategory.RULE, '구간 2', None, '다음', 0.7, 1),
    ]

    unique_hits = deduplicate_hits(hits)

    assert [(hit.document_id, hit.location) for hit in unique_hits] == [
        ('doc-1', '구간 1'),
        ('doc-1', '구간 2'),
    ]
    assert unique_hits[0].snippet == '첫번째'


def test_is_enumeration_query_detects_table_style_request() -> None:
    assert is_enumeration_query('직급별 승진 소요년수를 표로 정리해줘.') is True
    assert is_enumeration_query('휴가 승인 흐름을 알려줘.') is False


def test_retrieval_window_expands_candidate_pool_for_procurement_questions() -> None:
    assert needs_wide_candidate_search('구매 시 비교견적이나 입찰이 필요한 기준을 정리해줘.') is True

    effective_top_k, candidate_count = retrieval_window(
        '구매 시 비교견적이나 입찰이 필요한 기준을 정리해줘.',
        top_k=5,
        rerank_candidates=12,
    )

    assert effective_top_k == 5
    assert candidate_count == 30


def test_retrieval_window_expands_top_k_for_travel_questions() -> None:
    assert needs_wide_top_k('여비 규정의 출장비 지급 기준을 요약해줘.') is True

    effective_top_k, candidate_count = retrieval_window(
        '여비 규정의 출장비 지급 기준을 요약해줘.',
        top_k=5,
        rerank_candidates=12,
    )

    assert effective_top_k == 8
    assert candidate_count == 30


def test_retrieval_window_keeps_default_window_for_non_card_audit_questions() -> None:
    assert needs_wide_candidate_search('감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘.') is False
    assert needs_wide_top_k('감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘.') is False

    effective_top_k, candidate_count = retrieval_window(
        '감사 대응을 위해 지출 증빙이 부족할 때 어떤 위험과 보완 조치가 필요한지 알려줘.',
        top_k=5,
        rerank_candidates=12,
    )

    assert effective_top_k == 5
    assert candidate_count == 12


def test_needs_targeted_expansion_detects_project_evidence_questions() -> None:
    assert needs_targeted_expansion('사업비 집행 전 반드시 확인해야 할 증빙 서류 목록은 무엇인가요') is True
    assert needs_targeted_expansion('연차휴가 사용 절차를 알려줘') is False


def test_retrieval_window_expands_targeted_questions() -> None:
    effective_top_k, candidate_count = retrieval_window(
        '교육훈련 규칙에 따라 직원 교육 계획 수립 시 반드시 포함해야 할 항목은 무엇인가요',
        top_k=5,
        rerank_candidates=12,
    )

    assert effective_top_k == 10
    assert candidate_count == 24


def test_title_matches_question_ignores_spaces() -> None:
    assert title_matches_question('여비 규정의 출장비 지급 기준을 요약해줘', '여비 규정') is True
    assert title_matches_question('차량 운행 기준을 알려줘', '취업규칙') is False


def test_snippet_is_weak_flags_appendix_style_chunks() -> None:
    assert snippet_is_weak('부칙 <2023.12.21.>') is True
    assert snippet_is_weak('※ 비고') is True
    assert snippet_is_weak('[시행 2023.12.21.]') is True
    assert snippet_is_weak('제10조 출장비 지급 기준은 다음과 같다.') is False


def test_prioritize_hits_demotes_weak_chunks_for_title_matched_query() -> None:
    hits = [
        SearchHit('doc-1', '여비 규정', 'travel.md', DocumentCategory.RULE, '구간 60', None, '부칙 <2023.8.1.>', 0.95, 0),
        SearchHit('doc-1', '여비 규정', 'travel.md', DocumentCategory.RULE, '구간 12', None, '제10조 출장비 지급 기준은 다음과 같다.', 0.82, 1),
        SearchHit('doc-2', '취업규칙', 'hr.md', DocumentCategory.RULE, '구간 3', None, '제5조 징계 절차', 0.99, 2),
    ]

    prioritized = prioritize_hits(hits, '여비 규정의 출장비 지급 기준을 요약해줘')

    assert prioritized[0].location == '구간 12'
    assert prioritized[1].location == '구간 60'
    assert prioritized[2].document_id == 'doc-2'


def test_aggregate_parent_hits_prefers_concentrated_title_matched_parent() -> None:
    hits = [
        SearchHit(
            'doc-1',
            '여비 규정',
            'travel.md',
            DocumentCategory.RULE,
            '제10조 제1항',
            None,
            '제10조 출장비 지급 기준은 다음과 같다.',
            0.82,
            0,
            child_id='child-1',
            parent_id='parent-1',
            path_key='제3장>제10조>제1항',
        ),
        SearchHit(
            'doc-1',
            '여비 규정',
            'travel.md',
            DocumentCategory.RULE,
            '제10조 제1항',
            None,
            '부칙 <2023.12.21.>',
            0.66,
            1,
            child_id='child-2',
            parent_id='parent-1',
            path_key='제3장>제10조>제1항',
            is_addendum=True,
        ),
        SearchHit(
            'doc-1',
            '취업규칙',
            'hr.md',
            DocumentCategory.RULE,
            '제5조',
            None,
            '제5조 징계 절차는 별도 규정에 따른다.',
            0.95,
            2,
            child_id='child-3',
            parent_id='parent-2',
            path_key='제1장>제5조>제1항',
        ),
    ]

    aggregated = aggregate_parent_hits(hits, '여비 규정 제10조 출장비 지급 기준을 요약해줘')

    assert [hit.parent_id for hit in aggregated] == ['parent-1', 'parent-2']
    assert aggregated[0].child_hit_count == 2
    assert aggregated[0].best_child_score == 0.82
    assert aggregated[0].representative_text == '제10조 출장비 지급 기준은 다음과 같다.'
    assert aggregated[0].aggregate_score >= aggregated[0].lexical_score
    assert aggregated[0].aggregate_score > aggregated[1].aggregate_score


def test_aggregate_parent_hits_penalizes_weak_parent_groups() -> None:
    hits = [
        SearchHit(
            'doc-1',
            '여비 규정',
            'travel.md',
            DocumentCategory.RULE,
            '제10조',
            None,
            '부칙 <2023.8.1.>',
            0.91,
            0,
            child_id='child-1',
            parent_id='parent-1',
            path_key='제3장>제10조>제1항',
            is_addendum=True,
        ),
        SearchHit(
            'doc-1',
            '여비 규정',
            'travel.md',
            DocumentCategory.RULE,
            '제10조',
            None,
            '[시행 2023.12.21.]',
            0.88,
            1,
            child_id='child-2',
            parent_id='parent-1',
            path_key='제3장>제10조>제1항',
            is_addendum=True,
        ),
        SearchHit(
            'doc-1',
            '여비 규정',
            'travel.md',
            DocumentCategory.RULE,
            '제10조',
            None,
            '제10조 출장비 지급 기준은 다음과 같다.',
            0.84,
            2,
            child_id='child-3',
            parent_id='parent-2',
            path_key='제3장>제10조>제1항',
        ),
    ]

    aggregated = aggregate_parent_hits(hits, '여비 규정 제10조 출장비 지급 기준을 알려줘')

    assert aggregated[0].parent_id == 'parent-2'
    assert aggregated[0].aggregate_score > aggregated[1].aggregate_score


def test_score_document_title_match_prefers_specific_title_overlap() -> None:
    from app.models.schemas import CategorySource, DocumentDomain, DocumentStatus, DocumentRecord
    from datetime import datetime, timezone

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

    from app.services.retrieval_utils import shortlist_documents_by_title

    shortlisted = shortlist_documents_by_title(
        '취업규칙에서 징계 절차를 단계별로 설명해줘',
        [record],
    )

    assert shortlisted == [record]


def test_score_document_title_match_handles_title_noise_and_particles() -> None:
    score = score_document_title_match(
        '취업규칙에서 징계 절차를 단계별로 설명해줘',
        '[3-18] 취업규칙(2026.1.1.)',
    )

    assert score >= 0.5


def test_shortlist_documents_by_title_prefers_exact_document_with_noisy_title() -> None:
    from app.models.schemas import CategorySource, DocumentDomain, DocumentStatus, DocumentRecord
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    target = DocumentRecord(
        id='doc-1',
        title='[3-18] 취업규칙(2026.1.1.)',
        filename='[3-18] 취업규칙(2026.1.1.).md',
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
    distractor = DocumentRecord(
        id='doc-2',
        title='[2-4] 인사 관리 규정(2025.10.24.)',
        filename='hr-rule.md',
        stored_filename='hr-rule.md',
        file_path='/tmp/hr-rule.md',
        category=DocumentCategory.RULE,
        category_source=CategorySource.AUTO,
        domain=DocumentDomain.OTHER,
        tags=[],
        status=DocumentStatus.READY,
        uploaded_at=now,
        updated_at=now,
    )

    shortlisted = shortlist_documents_by_title(
        '취업규칙에서 징계 절차를 단계별로 설명해줘',
        [distractor, target],
    )

    assert shortlisted[0].id == target.id


def test_score_document_title_match_prefers_specific_compound_title_tokens() -> None:
    question = '\ubc95\uc778\ucc28\ub7c9 \uad00\ub9ac \uaddc\uce59\uc5d0\uc11c \ucc28\ub7c9 \uc6b4\ud589\uacfc \uad00\ub9ac \ucc45\uc784 \uae30\uc900\uc744 \uc694\uc57d\ud574\uc918'

    target_score = score_document_title_match(question, '[3-11] \ubc95\uc778\ucc28\ub7c9 \uad00\ub9ac \uaddc\uce59(2024.12.19.)')
    distractor_score = score_document_title_match(question, '[3-5] \uc778\uc0ac \uad00\ub9ac \uaddc\uce59(2026.1.23.)')

    assert target_score > distractor_score
