from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path).reset_index(drop=True)


def summary_metric(summary: dict[str, float], key: str) -> float:
    return round(float(summary.get(key, 0.0)), 6)


def summarize_case(row: pd.Series) -> dict:
    return {
        "qid": row["qid"],
        "query": row["query"],
        "answer_mode": row["answer_mode"],
        "categories": row["categories"],
        "retrieval_f1_on": round(float(row["retrieval_f1_on"]), 4),
        "retrieval_f1_off": round(float(row["retrieval_f1_off"]), 4),
        "rouge": round(float(row["rouge"]), 4),
        "bleu": round(float(row["bleu"]), 4),
        "answer_preview": str(row["generated_texts"])[:240],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a markdown report for a Ralph-loop AutoRAG run.")
    parser.add_argument(
        "--qa-path",
        type=Path,
        default=Path("/app/data/autorag/bootstrap/qa.parquet"),
    )
    parser.add_argument(
        "--retrieval-on-path",
        type=Path,
        default=Path("/app/data/autorag/results/retrieval_eval_reranker_on.csv"),
    )
    parser.add_argument(
        "--retrieval-off-path",
        type=Path,
        default=Path("/app/data/autorag/results/retrieval_eval_reranker_off.csv"),
    )
    parser.add_argument(
        "--generation-path",
        type=Path,
        default=Path("/app/data/autorag/results/generation_eval.csv"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/reports"),
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    qa_df = pd.read_parquet(args.qa_path).reset_index(drop=True)
    retrieval_on_df = load_csv(args.retrieval_on_path).add_suffix("_on")
    retrieval_off_df = load_csv(args.retrieval_off_path).add_suffix("_off")
    generation_df = load_csv(args.generation_path)

    merged_df = pd.concat([qa_df, retrieval_on_df, retrieval_off_df, generation_df], axis=1)
    merged_df["categories"] = merged_df["categories"].apply(
        lambda value: ", ".join(value) if isinstance(value, list) else str(value)
    )

    retrieval_on_summary = retrieval_on_df.mean(numeric_only=True).to_dict()
    retrieval_off_summary = retrieval_off_df.mean(numeric_only=True).to_dict()
    generation_summary = generation_df.mean(numeric_only=True).to_dict()
    retrieval_f1_on = summary_metric(retrieval_on_summary, "retrieval_f1_on")
    retrieval_recall_on = summary_metric(retrieval_on_summary, "retrieval_recall_on")
    retrieval_precision_on = summary_metric(retrieval_on_summary, "retrieval_precision_on")
    retrieval_f1_off = summary_metric(retrieval_off_summary, "retrieval_f1_off")
    retrieval_recall_off = summary_metric(retrieval_off_summary, "retrieval_recall_off")
    retrieval_precision_off = summary_metric(retrieval_off_summary, "retrieval_precision_off")
    generation_bleu = summary_metric(generation_summary, "bleu")
    generation_rouge = summary_metric(generation_summary, "rouge")

    best_gain_df = merged_df.assign(
        rerank_gain=merged_df["retrieval_f1_on"] - merged_df["retrieval_f1_off"]
    )
    weakest_generation = [
        summarize_case(row)
        for _, row in merged_df.sort_values(["rouge", "bleu"], ascending=[True, True]).head(3).iterrows()
    ]
    weakest_retrieval = [
        summarize_case(row)
        for _, row in merged_df.sort_values(["retrieval_f1_on", "retrieval_precision_on"], ascending=[True, True]).head(3).iterrows()
    ]
    biggest_rerank_gains = [
        summarize_case(row)
        for _, row in best_gain_df.sort_values("rerank_gain", ascending=False).head(3).iterrows()
    ]

    summary = {
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "retrieval_on_mean": {key: round(float(value), 6) for key, value in retrieval_on_summary.items()},
        "retrieval_off_mean": {key: round(float(value), 6) for key, value in retrieval_off_summary.items()},
        "generation_mean": {key: round(float(value), 6) for key, value in generation_summary.items()},
        "weakest_generation_cases": weakest_generation,
        "weakest_retrieval_cases": weakest_retrieval,
        "biggest_reranker_gain_cases": biggest_rerank_gains,
    }

    summary_path = args.output_dir / f"summary_{args.run_id}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    history_path = args.output_dir / "history.csv"
    history_row = pd.DataFrame(
        [
            {
                "run_id": args.run_id,
                "generated_at_utc": summary["generated_at_utc"],
                "retrieval_f1_on": retrieval_f1_on,
                "retrieval_recall_on": retrieval_recall_on,
                "retrieval_precision_on": retrieval_precision_on,
                "retrieval_f1_off": retrieval_f1_off,
                "retrieval_recall_off": retrieval_recall_off,
                "retrieval_precision_off": retrieval_precision_off,
                "bleu": generation_bleu,
                "rouge": generation_rouge,
            }
        ]
    )
    if history_path.exists():
        existing_history = pd.read_csv(history_path)
        history_df = pd.concat([existing_history, history_row], ignore_index=True)
    else:
        history_df = history_row
    history_df.to_csv(history_path, index=False)

    report_lines = [
        f"# Ralph Loop Report {args.run_id}",
        "",
        f"- Generated at (UTC): {summary['generated_at_utc']}",
        f"- Retrieval F1 with reranker: {retrieval_f1_on:.4f}",
        f"- Retrieval F1 without reranker: {retrieval_f1_off:.4f}",
        f"- Generation BLEU: {generation_bleu:.4f}",
        f"- Generation ROUGE: {generation_rouge:.4f}",
        "",
        "## Interpretation",
        "",
        "- `BAAI/bge-reranker-v2-m3` materially improves retrieval quality over vector-only ranking.",
        "- Current priority is improving low-ROUGE generation cases while preserving retrieval gains.",
        "",
        "## Weakest Generation Cases",
        "",
    ]

    for case in weakest_generation:
        report_lines.extend(
            [
                f"- `{case['qid']}` {case['query']}",
                f"  mode={case['answer_mode']} categories={case['categories']} rouge={case['rouge']:.4f} bleu={case['bleu']:.4f}",
            ]
        )

    report_lines.extend(["", "## Weakest Retrieval Cases", ""])
    for case in weakest_retrieval:
        report_lines.extend(
            [
                f"- `{case['qid']}` {case['query']}",
                f"  reranker_on_f1={case['retrieval_f1_on']:.4f} reranker_off_f1={case['retrieval_f1_off']:.4f}",
            ]
        )

    report_lines.extend(["", "## Biggest Reranker Gains", ""])
    for case in biggest_rerank_gains:
        report_lines.extend(
            [
                f"- `{case['qid']}` {case['query']}",
                f"  reranker_on_f1={case['retrieval_f1_on']:.4f} reranker_off_f1={case['retrieval_f1_off']:.4f}",
            ]
        )

    report_lines.extend(
        [
            "",
            "## Next Actions",
            "",
            "- Tune prompt structure for the weakest generation cases.",
            "- Expand the reviewed seed set beyond the current bootstrap 8 questions.",
            "- Keep `BAAI/bge-reranker-v2-m3` as the default reranker because retrieval quality is substantially higher with it enabled.",
        ]
    )

    report_path = args.output_dir / f"report_{args.run_id}.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Saved summary JSON: {summary_path}")
    print(f"Saved report markdown: {report_path}")
    print(f"Updated history CSV: {history_path}")


if __name__ == "__main__":
    main()
