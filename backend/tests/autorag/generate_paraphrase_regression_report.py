from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.dependencies import get_chat_service
from app.models.schemas import AnswerMode, ChatRequest, DocumentCategory
from app.services.answer_templates import match_answer_template
from gold_dataset_utils import build_retrieval_gt_from_citations
from paraphrase_regression_utils import (
    answer_similarity_score,
    citation_panel_is_clean,
    classify_regression_status,
    extract_answer_references,
    flatten_retrieval_gt,
    retrieval_overlap_metrics,
)


def load_review_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"Review queue JSON does not contain rows: {path}")
    return payload


def choose_generation_gt(row: dict[str, Any]) -> str:
    reviewed = row.get("reviewed_generation_gt", [])
    if isinstance(reviewed, list):
        for item in reviewed:
            normalized = str(item).strip()
            if normalized:
                return normalized
    bootstrap = row.get("bootstrap_generation_gt", [])
    if isinstance(bootstrap, list):
        for item in bootstrap:
            normalized = str(item).strip()
            if normalized:
                return normalized
    return ""


def choose_retrieval_gt(row: dict[str, Any]) -> list[str]:
    reviewed = flatten_retrieval_gt(row.get("reviewed_retrieval_gt", []))
    if reviewed:
        return reviewed
    return flatten_retrieval_gt(row.get("bootstrap_retrieval_gt", []))


async def evaluate_rows(review_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    service = get_chat_service()
    results: list[dict[str, Any]] = []

    for row in review_rows:
        answer_mode = AnswerMode(str(row["answer_mode"]))
        response = await service.answer(
            ChatRequest(
                question=str(row["query"]),
                categories=[DocumentCategory(value) for value in row.get("categories", [])],
                answer_mode=answer_mode,
            )
        )

        expected_retrieval_gt = choose_retrieval_gt(row)
        current_retrieval_gt = flatten_retrieval_gt(build_retrieval_gt_from_citations(response.citations))
        retrieval_metrics = retrieval_overlap_metrics(expected_retrieval_gt, current_retrieval_gt)

        baseline_answer = choose_generation_gt(row)
        answer_similarity = answer_similarity_score(response.answer, baseline_answer)
        references = extract_answer_references(response.answer)
        citation_clean = citation_panel_is_clean(response.answer, len(response.citations))
        template_id = match_answer_template(str(row["query"]), answer_mode)
        status = classify_regression_status(
            retrieval_f1=float(retrieval_metrics["f1"]),
            answer_similarity=answer_similarity,
            citation_panel_clean=citation_clean,
            citation_count=len(response.citations),
        )

        results.append(
            {
                "qid": str(row["qid"]),
                "query": str(row["query"]),
                "answer_mode": answer_mode.value,
                "categories": list(row.get("categories", [])),
                "template_id": template_id,
                "status": status,
                "answer_similarity": answer_similarity,
                "citation_panel_clean": citation_clean,
                "citation_count": len(response.citations),
                "referenced_citation_count": len(references),
                "confidence": response.confidence,
                "retrieval_metrics": retrieval_metrics,
                "expected_retrieval_gt": expected_retrieval_gt,
                "current_retrieval_gt": current_retrieval_gt,
                "current_answer": response.answer,
                "baseline_answer": baseline_answer,
                "current_citations": [citation.model_dump(mode="json") for citation in response.citations],
            }
        )

    return results


def markdown_report(*, run_id: str, source_path: Path, rows: list[dict[str, Any]]) -> str:
    status_counts = Counter(row["status"] for row in rows)
    mode_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        mode_counts[row["answer_mode"]][row["status"]] += 1

    lines = [
        f"# Paraphrase Regression Report {run_id}",
        "",
        f"- Review queue: `{source_path}`",
        f"- Total rows: {len(rows)}",
        f"- ok: {status_counts.get('ok', 0)}",
        f"- needs_review: {status_counts.get('needs_review', 0)}",
        f"- high_risk: {status_counts.get('high_risk', 0)}",
        "",
        "## By Mode",
        "",
    ]

    for answer_mode in sorted(mode_counts):
        lines.append(
            f"- `{answer_mode}` ok={mode_counts[answer_mode].get('ok', 0)} needs_review={mode_counts[answer_mode].get('needs_review', 0)} high_risk={mode_counts[answer_mode].get('high_risk', 0)}"
        )

    def add_section(title: str, filtered_rows: list[dict[str, Any]]) -> None:
        lines.extend(["", f"## {title}", ""])
        if not filtered_rows:
            lines.append("- none")
            return
        for row in filtered_rows:
            retrieval = row["retrieval_metrics"]
            lines.extend(
                [
                    f"- `{row['qid']}` [{row['answer_mode']}] {row['query']}",
                    f"  status={row['status']} template={row['template_id'] or '-'} confidence={row['confidence']} similarity={row['answer_similarity']:.4f} retrieval_f1={retrieval['f1']:.4f}",
                    f"  citation_panel_clean={row['citation_panel_clean']} citations={row['citation_count']} referenced={row['referenced_citation_count']}",
                    f"  expected_ids={row['expected_retrieval_gt'][:4]}",
                    f"  current_ids={row['current_retrieval_gt'][:4]}",
                ]
            )

    sorted_rows = sorted(
        rows,
        key=lambda row: (row["status"] != "high_risk", row["status"] != "needs_review", row["answer_similarity"]),
    )
    add_section("High Risk Cases", [row for row in sorted_rows if row["status"] == "high_risk"][:12])
    add_section("Needs Review Cases", [row for row in sorted_rows if row["status"] == "needs_review"][:12])

    clean_rows = [row for row in rows if not row["citation_panel_clean"]]
    lines.extend(["", "## Citation Panel Issues", ""])
    if clean_rows:
        for row in clean_rows[:12]:
            lines.append(
                f"- `{row['qid']}` [{row['answer_mode']}] citations={row['citation_count']} referenced={row['referenced_citation_count']} query={row['query']}"
            )
    else:
        lines.append("- none")

    return "\n".join(lines).rstrip() + "\n"


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run paraphrase regression checks against a review queue.")
    parser.add_argument(
        "--review-queue-path",
        type=Path,
        required=True,
        help="Path to review_queue_<run>.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/paraphrase"),
        help="Directory where paraphrase regression artifacts will be written.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        help="Run id suffix used in output filenames.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    review_payload = load_review_payload(args.review_queue_path)
    rows = await evaluate_rows(review_payload["rows"])

    payload = {
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "review_queue_path": str(args.review_queue_path),
        "source_run_id": review_payload.get("run_id", ""),
        "rows": rows,
        "summary": {
            "total_rows": len(rows),
            "ok": sum(1 for row in rows if row["status"] == "ok"),
            "needs_review": sum(1 for row in rows if row["status"] == "needs_review"),
            "high_risk": sum(1 for row in rows if row["status"] == "high_risk"),
            "citation_panel_issues": sum(1 for row in rows if not row["citation_panel_clean"]),
        },
    }

    json_path = args.output_dir / f"paraphrase_regression_{args.run_id}.json"
    md_path = args.output_dir / f"paraphrase_regression_{args.run_id}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(
        markdown_report(run_id=args.run_id, source_path=args.review_queue_path, rows=rows),
        encoding="utf-8",
    )

    print(f"Paraphrase rows: {len(rows)}")
    print(f"Paraphrase regression JSON: {json_path}")
    print(f"Paraphrase regression markdown: {md_path}")


if __name__ == "__main__":
    asyncio.run(main())
