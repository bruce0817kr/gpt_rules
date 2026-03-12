from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gold_dataset_utils import apply_review_decisions


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_decisions(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    if isinstance(payload, dict) and isinstance(payload.get("decisions"), list):
        items = payload["decisions"]
    elif isinstance(payload, list):
        items = payload
    else:
        raise ValueError(f"Unsupported decisions payload: {path}")

    decisions: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        qid = str(item.get("qid", "")).strip()
        if not qid:
            continue
        decisions[qid] = item
    return decisions


def load_review_payload(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"Review queue JSON does not contain rows: {path}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply review decisions to source review queue files.")
    parser.add_argument(
        "--decisions-path",
        type=Path,
        required=True,
        help="Path to review decision JSON.",
    )
    parser.add_argument(
        "--review-dir",
        type=Path,
        default=Path("backend/data/autorag/review"),
        help="Directory containing review_queue_*.json and feedback_review_queue_*.json.",
    )
    parser.add_argument(
        "--patterns",
        nargs="*",
        default=["review_queue_*.json", "feedback_review_queue_*.json"],
        help="Glob patterns used to discover source review queue files.",
    )
    args = parser.parse_args()

    decisions = load_decisions(args.decisions_path)
    remaining_qids = set(decisions)
    touched_files: list[dict[str, Any]] = []

    for pattern in args.patterns:
        for path in sorted(args.review_dir.glob(pattern)):
            payload = load_review_payload(path)
            updated_rows, touched_qids = apply_review_decisions(payload["rows"], decisions)
            if not touched_qids:
                continue

            payload["rows"] = updated_rows
            payload["review_decision_applied_at_utc"] = datetime.now(timezone.utc).isoformat()
            payload["review_decision_source"] = str(args.decisions_path)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            touched_files.append(
                {
                    "path": str(path),
                    "touched_qids": touched_qids,
                }
            )
            remaining_qids -= set(touched_qids)

    if remaining_qids:
        raise RuntimeError(f"Decisions did not match any source review rows: {sorted(remaining_qids)}")

    print(f"Applied decisions: {len(decisions)}")
    for touched in touched_files:
        print(f"- {touched['path']}: {len(touched['touched_qids'])} rows")


if __name__ == "__main__":
    main()
