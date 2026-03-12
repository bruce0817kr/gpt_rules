from __future__ import annotations

import json
import re
import hashlib
from datetime import datetime, timezone

import requests

from app.config import Settings
from app.models.schemas import DocumentCategory, DocumentRecord
from app.services.catalog import DocumentCatalog
from app.services.ingestion import DocumentIngestionService


class LawSyncService:
    SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
    BODY_URL = "https://www.law.go.kr/DRF/lawService.do"

    def __init__(
        self,
        settings: Settings,
        catalog: DocumentCatalog,
        ingestion: DocumentIngestionService,
    ) -> None:
        self.settings = settings
        self.catalog = catalog
        self.ingestion = ingestion

    def import_law_by_name(self, law_name: str) -> DocumentRecord:
        law_name = law_name.strip()
        if not law_name:
            raise ValueError("법령명을 입력해야 합니다.")

        search_item = self._search_law(law_name)
        law_title = self._pick(search_item, "법령명한글", "법령명")
        mst = self._pick(search_item, "법령일련번호")
        efyd = self._pick(search_item, "시행일자")
        law_id = search_item.get("법령ID")
        body = self._fetch_law_body(mst, efyd, law_id)

        storage_dir = self.settings.data_dir / "law_md"
        safe_name = self._safe_name(law_title)
        json_path = storage_dir / f"{safe_name}.json"
        md_path = storage_dir / f"{safe_name}.md"

        markdown = self._render_markdown(body, search_item)
        content_hash = self._content_hash(body)
        source_version = efyd
        source_url = f"https://www.law.go.kr/법령/{requests.utils.requote_uri(law_title)}"

        existing_by_identity = self.catalog.find_by_source_identity(mst, source_version)
        if existing_by_identity and existing_by_identity.content_hash == content_hash:
            return existing_by_identity

        json_path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(markdown, encoding="utf-8")

        existing = existing_by_identity or self.catalog.find_by_filename(md_path.name)
        if existing is not None:
            self.ingestion.delete_document(existing.id)

        return self.ingestion.ingest_saved_file(
            source_path=md_path,
            original_filename=md_path.name,
            title=law_title,
            category=DocumentCategory.LAW,
            tags=["law", "openapi", "on-demand"],
            source_id=mst,
            source_version=source_version,
            source_url=source_url,
            content_hash=content_hash,
        )

    def _search_law(self, law_name: str) -> dict[str, str]:
        response = requests.get(
            self.SEARCH_URL,
            params={
                "OC": self.settings.law_oc,
                "target": "eflaw",
                "type": "JSON",
                "query": law_name,
                "nw": 3,
                "display": 20,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = json.loads(response.content.decode("utf-8"))
        laws = payload.get("LawSearch", {}).get("law", [])
        if not laws:
            raise ValueError(f"'{law_name}'에 해당하는 법령을 찾지 못했습니다.")

        exact_match = next((law for law in laws if self._pick(law, "법령명한글", "법령명") == law_name), None)
        return exact_match or laws[0]

    def _fetch_law_body(self, mst: str, efyd: str, law_id: str | None) -> dict[str, object]:
        params = {
            "OC": self.settings.law_oc,
            "target": "eflaw",
            "type": "JSON",
        }
        if law_id:
            params["ID"] = law_id
        else:
            params["MST"] = mst
            params["efYd"] = efyd

        response = requests.get(
            self.BODY_URL,
            params=params,
            timeout=120,
        )
        response.raise_for_status()
        return json.loads(response.content.decode("utf-8"))

    def _render_markdown(self, payload: dict[str, object], search_item: dict[str, str]) -> str:
        law_title = self._pick(search_item, "법령명한글", "법령명")
        header = [
            f"# {law_title}",
            "",
            f"- 수집시각: {datetime.now(timezone.utc).isoformat()}",
            f"- 시행일자: {search_item.get('시행일자', '')}",
            f"- 공포일자: {search_item.get('공포일자', '')}",
            f"- 공포번호: {search_item.get('공포번호', '')}",
            f"- 법령일련번호(MST): {search_item.get('법령일련번호', '')}",
            f"- 출처: https://www.law.go.kr/법령/{requests.utils.requote_uri(law_title)}",
            "",
        ]
        body_lines: list[str] = []
        self._flatten(payload.get("법령", payload), body_lines, level=2)
        return "\n".join(header + body_lines).strip() + "\n"

    def _flatten(self, value: object, lines: list[str], level: int) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if isinstance(nested, (dict, list)):
                    lines.append(f"{'#' * min(level, 6)} {key}")
                    lines.append("")
                    self._flatten(nested, lines, level + 1)
                elif nested:
                    lines.append(f"- {key}: {nested}")
            if lines and lines[-1] != "":
                lines.append("")
            return

        if isinstance(value, list):
            for item in value:
                self._flatten(item, lines, level)
            return

        if isinstance(value, str):
            text = re.sub(r"\s+", " ", value).strip()
            if text:
                if re.match(r"^제\d+조", text) or text.startswith("별표"):
                    lines.append(f"## {text}")
                else:
                    lines.append(text)
            return

        if value is not None:
            lines.append(str(value))

    def _safe_name(self, law_name: str) -> str:
        cleaned = re.sub(r'[\\/:*?"<>|]+', '_', law_name).strip()
        return cleaned or 'law'

    def _content_hash(self, payload: dict[str, object]) -> str:
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def _pick(self, mapping: dict[str, str], *keys: str) -> str:
        for key in keys:
            value = mapping.get(key)
            if value:
                return value
        raise KeyError(keys[0])
