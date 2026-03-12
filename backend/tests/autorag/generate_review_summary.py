from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gold_dataset_utils import (
    load_json_cases,
    question_overlap_summary,
    suggest_review_action,
)


def load_review_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"Review queue JSON does not contain rows: {path}")
    return payload


def bootstrap_titles(row: dict[str, Any], limit: int = 2) -> list[str]:
    citations = row.get("bootstrap_citations", [])
    titles: list[str] = []
    for citation in citations:
        title = str(citation.get("title", "")).strip()
        location = str(citation.get("location", "")).strip()
        if not title:
            continue
        display = f"{title} / {location}" if location else title
        if display not in titles:
            titles.append(display)
        if len(titles) >= limit:
            break
    return titles


def build_summary_rows(seed_cases: list[dict[str, Any]], review_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary_rows: list[dict[str, Any]] = []

    for index, row in enumerate(review_rows):
        other_candidates = [candidate for i, candidate in enumerate(review_rows) if i != index]
        seed_overlap = question_overlap_summary(
            row["query"],
            answer_mode=row["answer_mode"],
            other_questions=seed_cases,
            question_key="question",
            id_key="id",
        )
        peer_overlap = question_overlap_summary(
            row["query"],
            answer_mode=row["answer_mode"],
            other_questions=other_candidates,
            question_key="query",
            id_key="qid",
        )
        action = suggest_review_action(seed_overlap, peer_overlap)

        summary_rows.append(
            {
                "qid": row["qid"],
                "query": row["query"],
                "answer_mode": row["answer_mode"],
                "categories": list(row.get("categories", [])),
                "candidate_note": row.get("candidate_note", ""),
                "suggested_action": action,
                "seed_overlap": seed_overlap,
                "peer_overlap": peer_overlap,
                "bootstrap_title_hints": bootstrap_titles(row),
            }
        )

    return summary_rows


def markdown_report(
    *,
    run_id: str,
    candidate_path: Path,
    review_queue_path: Path,
    summary_rows: list[dict[str, Any]],
) -> str:
    action_counts = Counter(row["suggested_action"] for row in summary_rows)
    grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in summary_rows:
        grouped_rows[row["answer_mode"]].append(row)

    lines = [
        f"# Gold Review Summary {run_id}",
        "",
        f"- Candidate file: `{candidate_path}`",
        f"- Review queue: `{review_queue_path}`",
        f"- Total candidates: {len(summary_rows)}",
        f"- Suggested `review_new`: {action_counts.get('review_new', 0)}",
        f"- Suggested `review_edit`: {action_counts.get('review_edit', 0)}",
        f"- Suggested `merge_or_skip`: {action_counts.get('merge_or_skip', 0)}",
        "",
        "## Review Guide",
        "",
        "- `review_new`: seed 질문과 겹침이 낮아 새 gold 후보로 우선 검토할 만한 질문",
        "- `review_edit`: 일부 중복/표현 겹침이 있어 wording 조정 후 유지할 가능성이 높은 질문",
        "- `merge_or_skip`: seed 또는 다른 후보와 매우 비슷해 통합 검토가 필요한 질문",
        "",
    ]

    for answer_mode in sorted(grouped_rows):
        lines.extend([f"## {answer_mode}", ""])
        for row in grouped_rows[answer_mode]:
            seed = row["seed_overlap"] or {}
            peer = row["peer_overlap"] or {}
            title_hints = "; ".join(row["bootstrap_title_hints"]) or "-"
            lines.extend(
                [
                    f"- `{row['qid']}` [{row['suggested_action']}] {row['query']}",
                    f"  categories={row['categories']} note={row['candidate_note']}",
                    f"  seed_overlap={seed.get('score', 0):.4f} seed_target={seed.get('id', '-')}: {seed.get('question', '-')}",
                    f"  peer_overlap={peer.get('score', 0):.4f} peer_target={peer.get('id', '-')}: {peer.get('question', '-')}",
                    f"  shared_keywords(seed)={seed.get('shared_keywords', [])} shared_keywords(peer)={peer.get('shared_keywords', [])}",
                    f"  bootstrap_titles={title_hints}",
                ]
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a review summary for persona-generated gold-set candidates.")
    parser.add_argument(
        "--candidate-path",
        type=Path,
        required=True,
        help="Path to candidate_cases_<run>.json.",
    )
    parser.add_argument(
        "--review-queue-path",
        type=Path,
        required=True,
        help="Path to review_queue_<run>.json.",
    )
    parser.add_argument(
        "--seed-path",
        type=Path,
        default=Path(__file__).with_name("seed_questions.json"),
        help="Path to the baseline seed questions JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/review"),
        help="Directory where summary artifacts will be written.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        help="Run id suffix used in output filenames.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    candidate_payload = json.loads(args.candidate_path.read_text(encoding="utf-8"))
    seed_cases = load_json_cases(args.seed_path)
    review_payload = load_review_payload(args.review_queue_path)
    summary_rows = build_summary_rows(seed_cases, review_payload["rows"])

    summary_payload = {
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_path": str(args.candidate_path),
        "review_queue_path": str(args.review_queue_path),
        "candidate_run_id": candidate_payload.get("run_id", ""),
        "rows": summary_rows,
    }

    json_path = args.output_dir / f"review_summary_{args.run_id}.json"
    md_path = args.output_dir / f"review_summary_{args.run_id}.md"
    json_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(
        markdown_report(
            run_id=args.run_id,
            candidate_path=args.candidate_path,
            review_queue_path=args.review_queue_path,
            summary_rows=summary_rows,
        ),
        encoding="utf-8",
    )

    print(f"Summary rows: {len(summary_rows)}")
    print(f"Review summary JSON: {json_path}")
    print(f"Review summary markdown: {md_path}")


if __name__ == "__main__":
    main()
