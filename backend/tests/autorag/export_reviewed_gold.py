from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from gold_dataset_utils import extract_approved_gold_rows

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover - depends on optional autorag requirements
    raise RuntimeError(
        "pandas is required to export reviewed gold. Install /app/tests/autorag/requirements.txt first."
    ) from exc


def load_review_rows(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("rows", [])
        if not isinstance(rows, list):
            raise ValueError(f"Review queue JSON does not contain a rows list: {path}")
        return rows

    if path.suffix.lower() == ".parquet":
        df = pd.read_parquet(path).reset_index(drop=True)
        return df.to_dict("records")

    raise ValueError(f"Unsupported review queue format: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export approved review queue rows as an AutoRAG gold qa.parquet.")
    parser.add_argument(
        "--review-queue-path",
        type=Path,
        required=True,
        help="Path to review_queue_<run>.json or .parquet.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/gold"),
        help="Directory where qa_gold.parquet will be written.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        help="Run id suffix used in output filenames.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    review_rows = load_review_rows(args.review_queue_path)
    gold_rows = extract_approved_gold_rows(review_rows)
    if not gold_rows:
        raise RuntimeError("No approved review rows found. Mark rows as approved before exporting gold.")

    qa_gold_path = args.output_dir / f"qa_gold_{args.run_id}.parquet"
    snapshot_path = args.output_dir / f"qa_gold_{args.run_id}.json"
    latest_path = args.output_dir / "qa_gold_latest.parquet"

    gold_df = pd.DataFrame(gold_rows).reset_index(drop=True)
    gold_df.to_parquet(qa_gold_path, index=False)
    gold_df.to_parquet(latest_path, index=False)
    snapshot_path.write_text(
        json.dumps(
            {
                "run_id": args.run_id,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "review_queue_path": str(args.review_queue_path),
                "rows": gold_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Approved gold rows: {len(gold_rows)}")
    print(f"Gold parquet: {qa_gold_path}")
    print(f"Latest gold parquet: {latest_path}")


if __name__ == "__main__":
    main()
