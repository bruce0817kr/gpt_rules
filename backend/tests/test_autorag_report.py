from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")


def load_generate_report_module():
    module_path = Path(__file__).parent / "autorag" / "generate_report.py"
    spec = importlib.util.spec_from_file_location("autorag_generate_report", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_report_uses_suffixed_metric_columns(tmp_path, monkeypatch) -> None:
    module = load_generate_report_module()

    qa_df = pd.DataFrame(
        [
            {
                "qid": "case-1",
                "query": "질문",
                "answer_mode": "standard",
                "categories": ["rule"],
            }
        ]
    )

    retrieval_on_path = tmp_path / "retrieval_on.csv"
    retrieval_off_path = tmp_path / "retrieval_off.csv"
    generation_path = tmp_path / "generation.csv"
    output_dir = tmp_path / "reports"

    pd.DataFrame(
        [
            {
                "retrieval_f1": 1.0,
                "retrieval_recall": 1.0,
                "retrieval_precision": 1.0,
            }
        ]
    ).to_csv(retrieval_on_path, index=False)
    pd.DataFrame(
        [
            {
                "retrieval_f1": 0.5,
                "retrieval_recall": 0.5,
                "retrieval_precision": 0.5,
            }
        ]
    ).to_csv(retrieval_off_path, index=False)
    pd.DataFrame(
        [
            {
                "generated_texts": "답변",
                "bleu": 0.75,
                "rouge": 0.5,
            }
        ]
    ).to_csv(generation_path, index=False)

    monkeypatch.setattr(module.pd, "read_parquet", lambda path: qa_df.copy())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "generate_report.py",
            "--qa-path",
            str(tmp_path / "qa.parquet"),
            "--retrieval-on-path",
            str(retrieval_on_path),
            "--retrieval-off-path",
            str(retrieval_off_path),
            "--generation-path",
            str(generation_path),
            "--output-dir",
            str(output_dir),
            "--run-id",
            "unit_test_run",
        ],
    )

    module.main()

    report_text = (output_dir / "report_unit_test_run.md").read_text(encoding="utf-8")
    history_df = pd.read_csv(output_dir / "history.csv")

    assert "Retrieval F1 with reranker: 1.0000" in report_text
    assert "Retrieval F1 without reranker: 0.5000" in report_text
    assert history_df.loc[0, "retrieval_f1_on"] == 1.0
    assert history_df.loc[0, "retrieval_f1_off"] == 0.5
    assert history_df.loc[0, "bleu"] == 0.75
    assert history_df.loc[0, "rouge"] == 0.5
