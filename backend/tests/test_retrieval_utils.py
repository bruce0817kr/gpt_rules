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
