from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from feedback_dataset_utils import (
    build_feedback_review_row,
    dedupe_bad_feedback,
    feedback_window_start,
    load_jsonl_records,
    merge_feedback_records,
    utc_now,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a review queue from recent bad user feedback.")
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
        default=Path("/app/data/autorag/review"),
        help="Directory where review queue artifacts will be written.",
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
    bad_rows = [row for row in merged_rows if row["rating"] == "bad"]
    deduped_rows = dedupe_bad_feedback(bad_rows)
    review_rows = [
        build_feedback_review_row(row, duplicate_count=int(row.get("duplicate_bad_count", 1)))
        for row in deduped_rows
    ]

    payload = {
        "run_id": args.run_id,
        "generated_at_utc": now.isoformat(),
        "lookback_days": args.lookback_days,
        "interactions_path": str(args.interactions_path),
        "feedback_path": str(args.feedback_path),
        "rows": review_rows,
    }

    json_path = args.output_dir / f"feedback_review_queue_{args.run_id}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Bad feedback review rows: {len(review_rows)}")
    print(f"Feedback review queue JSON: {json_path}")


if __name__ == "__main__":
    main()
