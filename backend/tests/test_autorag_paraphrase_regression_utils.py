from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    module_path = Path(__file__).parent / "autorag" / "paraphrase_regression_utils.py"
    spec = importlib.util.spec_from_file_location("autorag_paraphrase_regression_utils", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_flatten_retrieval_gt_deduplicates_nested_values() -> None:
    module = load_module()

    flattened = module.flatten_retrieval_gt(
        [["doc-1::구간 1"], ["doc-2::구간 2", "doc-1::구간 1"], "doc-3::구간 3"]
    )

    assert flattened == ["doc-1::구간 1", "doc-2::구간 2", "doc-3::구간 3"]


def test_retrieval_overlap_metrics_computes_f1() -> None:
    module = load_module()

    metrics = module.retrieval_overlap_metrics(
        ["doc-1::구간 1", "doc-2::구간 2"],
        ["doc-2::구간 2", "doc-3::구간 3"],
    )

    assert metrics == {
        "expected_count": 2.0,
        "actual_count": 2.0,
        "overlap_count": 1.0,
        "precision": 0.5,
        "recall": 0.5,
        "f1": 0.5,
    }


def test_citation_panel_is_clean_requires_dense_reference_order() -> None:
    module = load_module()

    assert module.citation_panel_is_clean("결론 [1][2] 근거 [3]", 3) is True
    assert module.citation_panel_is_clean("결론 [2][3]", 2) is False
    assert module.citation_panel_is_clean("결론 [1][3]", 2) is False


def test_classify_regression_status_distinguishes_high_risk_and_review() -> None:
    module = load_module()

    assert (
        module.classify_regression_status(
            retrieval_f1=0.92,
            answer_similarity=0.81,
            citation_panel_clean=True,
            citation_count=4,
        )
        == "ok"
    )
    assert (
        module.classify_regression_status(
            retrieval_f1=0.74,
            answer_similarity=0.81,
            citation_panel_clean=True,
            citation_count=4,
        )
        == "needs_review"
    )
    assert (
        module.classify_regression_status(
            retrieval_f1=0.92,
            answer_similarity=0.81,
            citation_panel_clean=False,
            citation_count=4,
        )
        == "high_risk"
    )
