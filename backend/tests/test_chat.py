from app.models.schemas import Citation, DocumentCategory
from app.services.chat import _extract_citation_indices, _prune_citations_to_answer


def make_citation(index: int) -> Citation:
    return Citation(
        index=index,
        document_id=f"doc-{index}",
        title=f"문서 {index}",
        filename=f"doc-{index}.md",
        category=DocumentCategory.RULE,
        location=f"구간 {index}",
        page_number=None,
        snippet=f"스니펫 {index}",
        score=0.9,
    )


def test_extract_citation_indices_preserves_first_appearance_order() -> None:
    answer = "결론 [4][3] 근거 [2][8] 반복 [4]"

    indices = _extract_citation_indices(answer)

    assert indices == [4, 3, 2, 8]


def test_prune_citations_to_answer_reorders_and_renumbers() -> None:
    citations = [make_citation(index) for index in range(1, 9)]
    answer = "결론 [4][3]\n근거 [2][8]\n반복 [4]"

    normalized_answer, pruned_citations = _prune_citations_to_answer(answer, citations)

    assert normalized_answer == "결론 [1][2]\n근거 [3][4]\n반복 [1]"
    assert [citation.index for citation in pruned_citations] == [1, 2, 3, 4]
    assert [citation.document_id for citation in pruned_citations] == ["doc-4", "doc-3", "doc-2", "doc-8"]


def test_prune_citations_to_answer_keeps_original_when_reference_is_missing() -> None:
    citations = [make_citation(index) for index in range(1, 4)]
    answer = "결론 [2][5]"

    normalized_answer, pruned_citations = _prune_citations_to_answer(answer, citations)

    assert normalized_answer == answer
    assert pruned_citations == citations
