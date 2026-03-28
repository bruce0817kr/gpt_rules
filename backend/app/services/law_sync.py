from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests

from app.config import Settings
from app.models.schemas import DocumentCategory, DocumentRecord
from app.services.catalog import DocumentCatalog
from app.services.ingestion import DocumentIngestionService

K_LAW_NAME = "\ubc95\ub839\uba85\ud55c\uae00"
K_LAW_NAME_FALLBACK = "\ubc95\ub839\uba85"
K_LAW_MST = "\ubc95\ub839\uc77c\ub828\ubc88\ud638"
K_EFFECTIVE_DATE = "\uc2dc\ud589\uc77c\uc790"
K_PROMULGATION_DATE = "\uacf5\ud3ec\uc77c\uc790"
K_PROMULGATION_NUMBER = "\uacf5\ud3ec\ubc88\ud638"
K_LAW_ID = "\ubc95\ub839ID"
K_LAW_ROOT = "\ubc95\ub839"

ARTICLE_RE = re.compile(r"^\uc81c\s*\d+\uc870")
ADDENDUM_RE = re.compile(r"^\ubd80\uce59")
APPENDIX_RE = re.compile(r"^(?:\ubcc4\ud45c\s*\d+|\ubcc4\uc9c0\s*\d+)")
NOISE_TEXT_RE = re.compile(r"^(?:0+|[0-9]{4,}|[|:\-=\s]+|[()\[\]○●▪▫■□]+)$")
PAREN_SHORT_TOKEN_RE = re.compile(r"^\([0-9A-Za-z가-힣]{1,3}\)$")

SKIP_KEYS = {
    "\ub9c1\ud06c",
    "link",
    "target",
    "content",
    "contents",
    "id",
    "ID",
    "MST",
    K_LAW_ID,
}


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
        law_title = self._pick(search_item, K_LAW_NAME, K_LAW_NAME_FALLBACK)
        mst = self._pick(search_item, K_LAW_MST)
        effective_date = self._pick(search_item, K_EFFECTIVE_DATE)
        law_id = search_item.get(K_LAW_ID)
        body = self._fetch_law_body(mst, effective_date, law_id)

        storage_dir = self.settings.data_dir / "law_md"
        storage_dir.mkdir(parents=True, exist_ok=True)
        safe_name = self._safe_name(law_title)
        json_path = storage_dir / f"{safe_name}.json"
        md_path = storage_dir / f"{safe_name}.md"

        markdown = self._render_markdown(body, search_item)
        content_hash = self._content_hash(body)
        source_url = f"https://www.law.go.kr/법령/{requests.utils.requote_uri(law_title)}"

        existing_by_identity = self.catalog.find_by_source_identity(mst, effective_date)
        if existing_by_identity and existing_by_identity.content_hash == content_hash:
            return existing_by_identity

        json_path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(markdown, encoding="utf-8")

        existing = existing_by_identity or self.catalog.find_by_filename(md_path.name)
        if existing is not None:
            self.ingestion.delete_document(existing.id)

        tags = [
            "law",
            "openapi",
            "on-demand",
            f"mst:{mst}",
            f"effective:{effective_date}",
            f"law-id:{law_id or ''}",
            f"law-name:{safe_name}",
        ]

        return self.ingestion.ingest_saved_file(
            source_path=md_path,
            original_filename=md_path.name,
            title=law_title,
            category=DocumentCategory.LAW,
            tags=tags,
            source_id=mst,
            source_version=effective_date,
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

        exact_match = next(
            (
                law
                for law in laws
                if self._pick(law, K_LAW_NAME, K_LAW_NAME_FALLBACK) == law_name
            ),
            None,
        )
        return exact_match or laws[0]

    def _fetch_law_body(self, mst: str, effective_date: str, law_id: str | None) -> dict[str, object]:
        params = {
            "OC": self.settings.law_oc,
            "target": "eflaw",
            "type": "JSON",
        }
        if law_id:
            params["ID"] = law_id
        else:
            params["MST"] = mst
            params["efYd"] = effective_date

        response = requests.get(self.BODY_URL, params=params, timeout=120)
        response.raise_for_status()
        return json.loads(response.content.decode("utf-8"))

    def _render_markdown(self, payload: dict[str, object], search_item: dict[str, str]) -> str:
        law_title = self._pick(search_item, K_LAW_NAME, K_LAW_NAME_FALLBACK)
        lines = [
            f"# {law_title}",
            "",
            "## Metadata",
            "",
            f"- law_name: {law_title}",
            f"- law_id: {search_item.get(K_LAW_ID, '')}",
            f"- synced_at: {datetime.now(timezone.utc).isoformat()}",
            f"- effective_date: {search_item.get(K_EFFECTIVE_DATE, '')}",
            f"- promulgation_date: {search_item.get(K_PROMULGATION_DATE, '')}",
            f"- promulgation_number: {search_item.get(K_PROMULGATION_NUMBER, '')}",
            f"- mst: {search_item.get(K_LAW_MST, '')}",
            f"- source_url: https://www.law.go.kr/법령/{requests.utils.requote_uri(law_title)}",
            "",
            "## Body",
            "",
        ]

        rendered_sections = self._flatten_sections(payload.get(K_LAW_ROOT, payload))
        if rendered_sections:
            lines.extend(rendered_sections)
        else:
            lines.append("_No structured law body could be extracted._")

        return "\n".join(lines).strip() + "\n"

    def _flatten_sections(self, value: object) -> list[str]:
        sections: list[str] = []
        self._walk(value, sections)
        return self._deduplicate_blank_lines(sections)

    def _walk(self, value: object, lines: list[str]) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if self._should_skip_key(key):
                    continue
                if isinstance(nested, (dict, list)):
                    self._walk(nested, lines)
                    continue
                self._append_scalar(key, nested, lines)
            return

        if isinstance(value, list):
            for item in value:
                if isinstance(item, list) and len(item) == 2 and all(isinstance(part, str) for part in item):
                    heading = self._clean_text(item[0])
                    body = self._clean_text(item[1])
                    self._append_pair(heading, body, lines)
                    continue
                self._walk(item, lines)
            return

        if isinstance(value, str):
            text = self._clean_text(value)
            if not self._is_noise_text(text):
                lines.append(text)
            return

        if value is not None:
            text = self._clean_text(str(value))
            if not self._is_noise_text(text):
                lines.append(text)

    def _append_scalar(self, key: str, value: object, lines: list[str]) -> None:
        text = self._clean_text(str(value))
        if self._is_noise_text(text):
            return

        if self._looks_like_heading(text):
            self._append_heading(text, lines)
            return

        key_text = self._clean_text(key)
        if self._is_noise_text(key_text):
            lines.append(text)
            return

        lines.append(f"- {key_text}: {text}")

    def _append_pair(self, heading: str, body: str, lines: list[str]) -> None:
        if self._is_noise_text(body):
            return
        if self._looks_like_heading(heading):
            self._append_heading(heading, lines)
            lines.append(body)
            lines.append("")
            return
        if heading and not self._is_noise_text(heading):
            lines.append(f"- {heading}: {body}")
            return
        lines.append(body)

    def _append_heading(self, text: str, lines: list[str]) -> None:
        level = "###" if ARTICLE_RE.match(text) or ADDENDUM_RE.match(text) or APPENDIX_RE.match(text) else "##"
        if lines and lines[-1] != "":
            lines.append("")
        lines.append(f"{level} {text}")
        lines.append("")

    def _looks_like_heading(self, text: str) -> bool:
        return bool(ARTICLE_RE.match(text) or ADDENDUM_RE.match(text) or APPENDIX_RE.match(text))

    def _should_skip_key(self, key: str) -> bool:
        key_text = self._clean_text(key).lower()
        return key in SKIP_KEYS or key_text in {item.lower() for item in SKIP_KEYS}

    def _clean_text(self, text: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        return normalized

    def _is_noise_text(self, text: str) -> bool:
        if not text:
            return True
        if NOISE_TEXT_RE.fullmatch(text):
            return True
        if PAREN_SHORT_TOKEN_RE.fullmatch(text):
            return True
        if text.startswith("http://") or text.startswith("https://"):
            return True
        if text.startswith("OpenAPI") or text.startswith("API:"):
            return True
        return False

    def _deduplicate_blank_lines(self, lines: Iterable[str]) -> list[str]:
        normalized: list[str] = []
        blank_pending = False
        for line in lines:
            if not line:
                if blank_pending:
                    continue
                blank_pending = True
                normalized.append("")
                continue
            blank_pending = False
            normalized.append(line)
        while normalized and normalized[-1] == "":
            normalized.pop()
        return normalized

    def _safe_name(self, law_name: str) -> str:
        cleaned = re.sub(r'[\\/:*?"<>|]+', "_", law_name).strip()
        return cleaned or "law"

    def _content_hash(self, payload: dict[str, object]) -> str:
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _pick(self, mapping: dict[str, str], *keys: str) -> str:
        for key in keys:
            value = mapping.get(key)
            if value:
                return value
        raise KeyError(keys[0])
