from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from app.dependencies import get_chat_service
from app.models.schemas import AnswerMode, ChatRequest, DocumentCategory
from gold_dataset_utils import build_review_row, load_json_cases

try:
    import pandas as pd
except ImportError:  # pragma: no cover - optional dependency on the base backend image
    pd = None


async def build_review_rows(cases: list[dict]) -> list[dict]:
    service = get_chat_service()
    rows: list[dict] = []

    for case in cases:
        response = await service.answer(
            ChatRequest(
                question=case["question"],
                categories=[DocumentCategory(value) for value in case["categories"]],
                answer_mode=AnswerMode(case["answer_mode"]),
            )
        )
        rows.append(build_review_row(case, response.answer, response.citations))

    return rows


async def main() -> None:
    parser = argparse.ArgumentParser(description="Build a human-review queue from persona-generated candidate questions.")
    parser.add_argument(
        "--cases-path",
        type=Path,
        required=True,
        help="Path to candidate question JSON produced by generate_persona_candidates.py.",
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
    cases = load_json_cases(args.cases_path)
    rows = await build_review_rows(cases)

    payload = {
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_cases_path": str(args.cases_path),
        "rows": rows,
    }

    json_path = args.output_dir / f"review_queue_{args.run_id}.json"
    parquet_path = args.output_dir / f"review_queue_{args.run_id}.parquet"
    source_snapshot_path = args.output_dir / f"review_source_cases_{args.run_id}.json"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if pd is not None:
        pd.DataFrame(rows).to_parquet(parquet_path, index=False)
    source_snapshot_path.write_text(args.cases_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Review rows: {len(rows)}")
    print(f"Review queue JSON: {json_path}")
    if pd is not None:
        print(f"Review queue parquet: {parquet_path}")
    else:
        print("Review queue parquet skipped: pandas is not installed in this container.")


if __name__ == "__main__":
    asyncio.run(main())
