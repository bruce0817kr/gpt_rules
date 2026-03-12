from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gold_dataset_utils import build_balanced_review_packets


def load_review_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"Review queue JSON does not contain rows: {path}")
    return payload


def markdown_report(*, run_id: str, review_queue_path: Path, packet_size: int, packets: list[dict[str, Any]]) -> str:
    lines = [
        f"# Review Packets {run_id}",
        "",
        f"- Review queue: `{review_queue_path}`",
        f"- Packet size: {packet_size}",
        f"- Packet count: {len(packets)}",
        "",
    ]

    for packet in packets:
        lines.extend(
            [
                f"## Packet {packet['packet_index']}",
                "",
                f"- Row count: {packet['row_count']}",
                f"- By mode: {packet['by_answer_mode']}",
                f"- By persona: {packet['by_persona']}",
                "",
            ]
        )
        for row in packet["rows"]:
            lines.append(
                "- "
                + f"`{row.get('qid', '')}` [{row.get('answer_mode', '')}] [{row.get('candidate_source', '')}] "
                + f"{row.get('query', '')}"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build balanced review packets from a merged review queue.")
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
        help="Directory where review packet artifacts will be written.",
    )
    parser.add_argument(
        "--packet-size",
        type=int,
        default=12,
        help="Maximum number of review rows in each packet.",
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
    packets = build_balanced_review_packets(payload["rows"], packet_size=args.packet_size)

    report_payload = {
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "review_queue_path": str(args.review_queue_path),
        "packet_size": args.packet_size,
        "packet_count": len(packets),
        "packets": packets,
    }

    json_path = args.output_dir / f"review_packets_{args.run_id}.json"
    md_path = args.output_dir / f"review_packets_{args.run_id}.md"
    json_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(
        markdown_report(
            run_id=args.run_id,
            review_queue_path=args.review_queue_path,
            packet_size=args.packet_size,
            packets=packets,
        ),
        encoding="utf-8",
    )

    print(f"Review packets: {len(packets)}")
    print(f"Review packets JSON: {json_path}")
    print(f"Review packets markdown: {md_path}")


if __name__ == "__main__":
    main()
