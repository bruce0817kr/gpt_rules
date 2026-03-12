from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("pandas")
pytest.importorskip("autorag")


def load_evaluate_module():
    module_path = Path(__file__).parent / "autorag" / "evaluate_current_rag.py"
    spec = importlib.util.spec_from_file_location("autorag_evaluate_current_rag", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalize_retrieval_gt_deduplicates_duplicate_chunk_ids() -> None:
    module = load_evaluate_module()

    normalized = module.normalize_retrieval_gt(
        [["doc-1::구간 1"], ["doc-1::구간 1"], ["doc-2::구간 2"]]
    )

    assert normalized == [["doc-1::구간 1"], ["doc-2::구간 2"]]
