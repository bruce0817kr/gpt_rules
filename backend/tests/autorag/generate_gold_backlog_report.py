from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gold_dataset_utils import review_backlog_snapshot


def load_review_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"Review queue JSON does not contain rows: {path}")
    return payload


def row_label(row: dict[str, Any]) -> str:
    persona = str(row.get("persona_id", "")).strip() or "unknown"
    source = str(row.get("candidate_source", "")).strip() or "unknown"
    status = str(row.get("review_status", "")).strip() or "unknown"
    return f"[{status}] [{source}] [{persona}]"


def markdown_report(*, run_id: str, review_queue_path: Path, rows: list[dict[str, Any]]) -> str:
    snapshot = review_backlog_snapshot(rows)
    pending_rows = [row for row in rows if str(row.get("review_status", "")).strip().lower() == "pending"]
    gold_ready_rows = [
        row
        for row in rows
        if str(row.get("review_status", "")).strip().lower() in {"approved", "approved_with_edits"}
        or bool(row.get("selected_for_gold", False))
    ]

    lines = [
        f"# Gold Backlog Report {run_id}",
        "",
        f"- Review queue: `{review_queue_path}`",
        f"- Total rows: {snapshot['total_rows']}",
        f"- Pending rows: {snapshot['pending_rows']}",
        f"- Approved rows: {snapshot['approved_rows']}",
        f"- Selected-for-gold rows: {snapshot['selected_for_gold_rows']}",
        f"- Gold-ready rows: {snapshot['gold_ready_rows']}",
        f"- Duplicate clusters: {snapshot['duplicate_clusters']}",
        "",
        "## By Source",
        "",
    ]

    for source, count in snapshot["by_source"].items():
        lines.append(f"- `{source}`: {count}")

    lines.extend(["", "## By Mode", ""])
    for answer_mode, count in snapshot["by_answer_mode"].items():
        lines.append(f"- `{answer_mode}`: {count}")

    lines.extend(["", "## By Persona", ""])
    for persona, count in snapshot["by_persona"].items():
        lines.append(f"- `{persona}`: {count}")

    lines.extend(["", "## Pending Review", ""])
    if pending_rows:
        for row in pending_rows[:20]:
            lines.extend(
                [
                    f"- `{row.get('qid', '')}` {row_label(row)} {row.get('query', '')}",
                    f"  note={row.get('candidate_note', '')} review_notes={row.get('review_notes', '')}",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Gold Ready", ""])
    if gold_ready_rows:
        for row in gold_ready_rows[:20]:
            lines.extend(
                [
                    f"- `{row.get('qid', '')}` {row_label(row)} {row.get('query', '')}",
                    f"  selected_for_gold={row.get('selected_for_gold', False)} merged_qids={row.get('merged_qids', [])}",
                ]
            )
    else:
        lines.append("- none")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an operational backlog report for merged gold review queues.")
    parser.add_argument(
        "--review-queue-path",
        type=Path,
        required=True,
        help="Path to merged_review_queue_<run>.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/review"),
        help="Directory where backlog report artifacts will be written.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        help="Run id suffix used in output filenames.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = load_review_payload(args.review_queue_path)
    rows = payload["rows"]
    snapshot = review_backlog_snapshot(rows)

    report_payload = {
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "review_queue_path": str(args.review_queue_path),
        "summary": snapshot,
        "rows": rows,
    }

    json_path = args.output_dir / f"gold_backlog_{args.run_id}.json"
    md_path = args.output_dir / f"gold_backlog_{args.run_id}.md"
    json_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(
        markdown_report(run_id=args.run_id, review_queue_path=args.review_queue_path, rows=rows),
        encoding="utf-8",
    )

    print(f"Gold backlog rows: {len(rows)}")
    print(f"Gold backlog JSON: {json_path}")
    print(f"Gold backlog markdown: {md_path}")


if __name__ == "__main__":
    main()
