from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gold_dataset_utils import merge_review_rows, review_backlog_snapshot


def load_review_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"Review queue JSON does not contain rows: {path}")
    return payload


def collect_review_paths(review_dir: Path, patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(review_dir.glob(pattern)):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge persona and feedback review queues into one backlog.")
    parser.add_argument(
        "--review-dir",
        type=Path,
        default=Path("/app/data/autorag/review"),
        help="Directory containing review_queue*.json and feedback_review_queue*.json files.",
    )
    parser.add_argument(
        "--patterns",
        nargs="*",
        default=["review_queue_*.json", "feedback_review_queue_*.json"],
        help="Glob patterns used to discover review queue JSON files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/review"),
        help="Directory where merged review artifacts will be written.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        help="Run id suffix used in output filenames.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    review_paths = collect_review_paths(args.review_dir, list(args.patterns))
    if not review_paths:
        raise RuntimeError(f"No review queues found in {args.review_dir} for patterns: {args.patterns}")

    source_rows: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    for path in review_paths:
        payload = load_review_payload(path)
        rows = payload["rows"]
        source_rows.extend(rows)
        source_summaries.append(
            {
                "path": str(path),
                "run_id": str(payload.get("run_id", "")),
                "row_count": len(rows),
            }
        )

    merged_rows = merge_review_rows(source_rows)
    snapshot = review_backlog_snapshot(merged_rows)

    merged_payload = {
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "review_dir": str(args.review_dir),
        "patterns": list(args.patterns),
        "source_files": source_summaries,
        "summary": snapshot,
        "rows": merged_rows,
    }

    merged_path = args.output_dir / f"merged_review_queue_{args.run_id}.json"
    merged_path.write_text(json.dumps(merged_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Source review rows: {len(source_rows)}")
    print(f"Merged review rows: {len(merged_rows)}")
    print(f"Merged review queue: {merged_path}")


if __name__ == "__main__":
    main()
