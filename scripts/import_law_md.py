from __future__ import annotations

import argparse
import json
from pathlib import Path
import hashlib

import requests


DEFAULT_DIR = Path(r"C:\Project\gpt_rules\Docs\MD\law_md")
DEFAULT_API = "http://localhost:8000/api"
EXCLUDED_FILES = {"OPENAPI_연동가이드.md"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Import or update converted law markdown files.")
    parser.add_argument("--law-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--api-base", default=DEFAULT_API)
    parser.add_argument("--replace-existing", action="store_true", default=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    law_dir = args.law_dir
    if not law_dir.exists():
      raise SystemExit(f"law_dir not found: {law_dir}")

    files = sorted(
        path for path in law_dir.glob("*.md") if path.name not in EXCLUDED_FILES
    )
    docs = requests.get(f"{args.api_base}/documents", timeout=120).json()
    existing_by_filename = {doc["filename"]: doc for doc in docs}

    summary: dict[str, object] = {
        "law_dir": str(law_dir),
        "candidates": len(files),
        "uploaded": [],
        "replaced": [],
        "skipped": [],
        "failed": [],
    }

    for path in files:
        companion_json = path.with_suffix('.json')
        source_id = None
        source_version = None
        source_url = None
        if companion_json.exists():
            try:
                payload = json.loads(companion_json.read_text(encoding='utf-8'))
                law_payload = payload.get('법령', payload)
                source_id = law_payload.get('법령일련번호') or law_payload.get('법령ID')
                source_version = law_payload.get('시행일자')
            except Exception:
                pass
        source_url = f"https://www.law.go.kr/법령/{requests.utils.requote_uri(path.stem)}"
        content_hash = hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest()

        existing = existing_by_filename.get(path.name)
        action_key = "uploaded"
        if existing is not None:
            action_key = "replaced"

        if args.dry_run:
            summary[action_key].append(path.name)
            continue

        if existing is not None and args.replace_existing:
            delete_response = requests.delete(
                f"{args.api_base}/documents/{existing['id']}",
                timeout=300,
            )
            if not delete_response.ok:
                summary["failed"].append({
                    "filename": path.name,
                    "stage": "delete",
                    "detail": delete_response.text[:300],
                })
                continue

        with path.open("rb") as file_handle:
            response = requests.post(
                f"{args.api_base}/documents/upload",
                files={"file": (path.name, file_handle, "text/markdown")},
                data={
                    "title": path.stem,
                    "category": "law",
                    "tags": "law,openapi,auto-import",
                },
                timeout=3600,
            )

        if response.ok:
            payload = response.json()
            summary[action_key].append(
                {
                    "filename": payload["filename"],
                    "category": payload["category"],
                    "status": payload["status"],
                }
            )
        else:
            summary["failed"].append(
                {
                    "filename": path.name,
                    "stage": "upload",
                    "detail": response.text[:300],
                }
            )

    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
