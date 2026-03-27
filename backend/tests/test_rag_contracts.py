from app.models.schemas import (
    AggregatedParentHit,
    AnswerabilityResult,
    ChunkSourceType,
    ChildChunkRecord,
    ParentChunkRecord,
    StructuredSection,
)


def test_structured_section_contract() -> None:
    section = StructuredSection(
        source_type=ChunkSourceType.ARTICLE,
        text='제10조 출장비 지급 기준은 다음과 같다.',
        chapter_label='제3장',
        section_label=None,
        article_label='제10조',
        paragraph_label='제1항',
        item_label=None,
        effective_date='2023-12-21',
        path_key='제3장>제10조>제1항',
        page_number=3,
        location='제10조 제1항',
        is_addendum=False,
        is_appendix=False,
    )

    assert section.source_type == ChunkSourceType.ARTICLE
    assert section.path_key == '제3장>제10조>제1항'


def test_parent_child_chunk_contracts() -> None:
    parent = ParentChunkRecord(
        parent_id='parent-1',
        document_id='doc-1',
        document_title='여비 규정',
        source_type=ChunkSourceType.ARTICLE,
        path_key='제3장>제10조',
        article_label='제10조',
        text='제10조 출장비 지급 기준은 다음과 같다.',
        representative_text='출장비 지급 기준은 다음과 같다.',
        child_ids=['child-1', 'child-2'],
        page_number=3,
        location='제10조',
        is_addendum=False,
        is_appendix=False,
    )
    child = ChildChunkRecord(
        child_id='child-1',
        parent_id='parent-1',
        document_id='doc-1',
        document_title='여비 규정',
        source_type=ChunkSourceType.ARTICLE,
        path_key='제3장>제10조>제1항',
        text='출장비 지급 기준은 다음과 같다.',
        page_number=3,
        location='제10조 제1항',
        chunk_index=0,
        is_addendum=False,
        is_appendix=False,
    )

    assert parent.child_ids == ['child-1', 'child-2']
    assert child.parent_id == parent.parent_id


def test_aggregated_parent_hit_and_answerability_contract() -> None:
    hit = AggregatedParentHit(
        parent_id='parent-1',
        document_id='doc-1',
        document_title='여비 규정',
        source_type=ChunkSourceType.ARTICLE,
        path_key='제3장>제10조',
        location='제10조',
        representative_text='출장비 지급 기준은 다음과 같다.',
        child_hit_count=2,
        best_child_score=0.91,
        lexical_score=0.74,
        aggregate_score=0.88,
        is_addendum=False,
        is_appendix=False,
    )
    result = AnswerabilityResult(
        is_answerable=True,
        confidence='medium',
        reason='top parent contains a matching article body',
        selected_parent_ids=['parent-1'],
    )

    assert hit.aggregate_score >= hit.lexical_score
    assert result.selected_parent_ids == ['parent-1']
