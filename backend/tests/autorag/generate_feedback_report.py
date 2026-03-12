from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from feedback_dataset_utils import (
    feedback_window_start,
    load_jsonl_records,
    merge_feedback_records,
    normalized_question_counts,
    reason_code_counts,
    template_id_counts,
    utc_now,
)


def markdown_report(*, run_id: str, lookback_days: int, merged_rows: list[dict]) -> str:
    rating_counts = Counter(row["rating"] for row in merged_rows)
    mode_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in merged_rows:
        mode_counts[row["answer_mode"]][row["rating"]] += 1

    bad_rows = [row for row in merged_rows if row["rating"] == "bad"]
    reason_rows = reason_code_counts(row["reason_codes"] for row in bad_rows if row["reason_codes"])
    template_rows = template_id_counts(bad_rows)
    repeated_bad_questions = normalized_question_counts(bad_rows)

    lines = [
        f"# Feedback Tuning Report {run_id}",
        "",
        f"- Lookback window: {lookback_days} days",
        f"- Total rated answers: {len(merged_rows)}",
        f"- Good: {rating_counts.get('good', 0)}",
        f"- Bad: {rating_counts.get('bad', 0)}",
        "",
        "## By Mode",
        "",
    ]

    for answer_mode in sorted(mode_counts):
        lines.append(
            f"- `{answer_mode}` good={mode_counts[answer_mode].get('good', 0)} bad={mode_counts[answer_mode].get('bad', 0)}"
        )

    lines.extend(["", "## Frequent Bad Reasons", ""])
    if reason_rows:
        for reason_code, count in reason_rows[:10]:
            lines.append(f"- `{reason_code}` {count}")
    else:
        lines.append("- No bad-reason codes yet.")

    lines.extend(["", "## Bad Templates", ""])
    if template_rows:
        for template_id, count in template_rows[:10]:
            lines.append(f"- `{template_id}` {count}")
    else:
        lines.append("- No bad template rows yet.")

    lines.extend(["", "## Repeated Bad Questions", ""])
    repeated_rows = [row for row in repeated_bad_questions if row[1] > 1]
    if repeated_rows:
        for question, count in repeated_rows[:10]:
            lines.append(f"- `{question}` {count}")
    else:
        lines.append("- No repeated bad questions yet.")

    lines.extend(["", "## Latest Bad Cases", ""])
    if bad_rows:
        for row in bad_rows[:12]:
            reason_text = ",".join(row["reason_codes"]) or "-"
            lines.append(
                f"- `{row['response_id']}` [{row['answer_mode']}] {row['question']} | reasons={reason_text} | confidence={row['confidence']}"
            )
    else:
        lines.append("- No bad feedback in the selected window.")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize recent user feedback for tuning review.")
    parser.add_argument(
        "--interactions-path",
        type=Path,
        default=Path("/app/data/feedback/chat_interactions.jsonl"),
        help="Path to chat interaction JSONL.",
    )
    parser.add_argument(
        "--feedback-path",
        type=Path,
        default=Path("/app/data/feedback/chat_feedback.jsonl"),
        help="Path to chat feedback JSONL.",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=3,
        help="How many recent days of feedback to include.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/feedback"),
        help="Directory where feedback report artifacts will be written.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        help="Run id suffix used in output filenames.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    since = feedback_window_start(now=now, lookback_days=args.lookback_days)
    interactions = load_jsonl_records(args.interactions_path)
    feedback_events = load_jsonl_records(args.feedback_path)
    merged_rows = merge_feedback_records(interactions, feedback_events, since=since)

    payload = {
        "run_id": args.run_id,
        "generated_at_utc": now.isoformat(),
        "lookback_days": args.lookback_days,
        "interactions_path": str(args.interactions_path),
        "feedback_path": str(args.feedback_path),
        "rows": merged_rows,
        "summary": {
            "rated_answers": len(merged_rows),
            "good": sum(1 for row in merged_rows if row["rating"] == "good"),
            "bad": sum(1 for row in merged_rows if row["rating"] == "bad"),
            "bad_template_counts": template_id_counts(row for row in merged_rows if row["rating"] == "bad"),
            "repeated_bad_questions": [
                {"question": question, "count": count}
                for question, count in normalized_question_counts(
                    row for row in merged_rows if row["rating"] == "bad"
                )
                if count > 1
            ],
        },
    }

    json_path = args.output_dir / f"feedback_report_{args.run_id}.json"
    md_path = args.output_dir / f"feedback_report_{args.run_id}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(
        markdown_report(run_id=args.run_id, lookback_days=args.lookback_days, merged_rows=merged_rows),
        encoding="utf-8",
    )

    print(f"Rated answers in window: {len(merged_rows)}")
    print(f"Feedback report JSON: {json_path}")
    print(f"Feedback report markdown: {md_path}")


if __name__ == "__main__":
    main()
