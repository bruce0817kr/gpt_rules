import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import fitz

from app.models.schemas import ChunkSourceType, StructuredSection


@dataclass(slots=True)
class ParsedSection:
    text: str
    location: str
    page_number: int | None = None


class DocumentParser:
    supported_suffixes = {".pdf", ".docx", ".txt", ".md", ".hwp", ".hwpx"}

    _CHAPTER_RE = re.compile(r"^(?P<label>제\s*\d+\s*장)(?:\s+(?P<title>.+))?$")
    _ARTICLE_RE = re.compile(r"^(?P<label>제\s*\d+\s*조)(?:\s*(?:\((?P<title>[^)]+)\)))?(?P<body>.*)$")
    _PARAGRAPH_RE = re.compile(r"^(?P<label>제\s*\d+\s*항)(?:\s*(?:\((?P<title>[^)]+)\)))?(?P<body>.*)$")
    _ITEM_PATTERNS = (
        re.compile(r"^(?P<label>\(\s*\d+\s*\))\s*(?P<body>.*)$"),
        re.compile(r"^(?P<label>\d+\.)\s*(?P<body>.*)$"),
        re.compile(r"^(?P<label>[가-힣]\.)\s*(?P<body>.*)$"),
        re.compile(r"^(?P<label>\(\s*[가-힣]\s*\))\s*(?P<body>.*)$"),
    )
    _ADDENDUM_RE = re.compile(r"^(?P<label>부칙)(?P<body>.*)$")
    _APPENDIX_RE = re.compile(
        r"^(?P<label>(?:별표\s*\d+(?:-\d+)?|별지\s*제?\s*\d+호(?:서식)?|서식\s*\d+))(?:\s+(?P<title>.+))?$"
    )
    _EFFECTIVE_DATE_RE = re.compile(r"<\s*(?P<year>\d{4})\.\s*(?P<month>\d{1,2})\.\s*(?P<day>\d{1,2})\.\s*>")

    def parse(self, file_path: Path) -> list[ParsedSection]:
        suffix = file_path.suffix.lower()
        if suffix not in self.supported_suffixes:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {suffix}")
        if suffix == ".pdf":
            sections = self._parse_pdf(file_path)
        elif suffix == ".docx":
            sections = self._parse_docx(file_path)
        elif suffix in {".hwp", ".hwpx"}:
            sections = self._parse_hwp_document(file_path)
        else:
            sections = self._parse_text(file_path)
        if not sections:
            raise ValueError("문서에서 추출 가능한 텍스트를 찾지 못했습니다.")
        return sections

    def parse_structured_sections(self, file_path: Path) -> list[StructuredSection]:
        basic_sections = self.parse(file_path)
        structured_sections: list[StructuredSection] = []

        current_chapter: str | None = None
        current_article_label: str | None = None
        current_article_lines: list[str] = []
        current_paragraph_label: str | None = None
        current_paragraph_lines: list[str] = []
        current_item_label: str | None = None
        current_item_lines: list[str] = []
        current_addendum_lines: list[str] = []
        current_appendix_label: str | None = None
        current_appendix_lines: list[str] = []
        current_page_number: int | None = None

        def emit_section(
            *,
            source_type: ChunkSourceType,
            text_lines: list[str],
            location: str,
            page_number: int | None,
            chapter_label: str | None = None,
            article_label: str | None = None,
            paragraph_label: str | None = None,
            item_label: str | None = None,
            effective_date: str | None = None,
            path_key: str | None = None,
            is_addendum: bool = False,
            is_appendix: bool = False,
        ) -> None:
            text = self._clean("\n".join(text_lines))
            if not text:
                return
            structured_sections.append(
                StructuredSection(
                    source_type=source_type,
                    text=text,
                    chapter_label=chapter_label,
                    section_label=None,
                    article_label=article_label,
                    paragraph_label=paragraph_label,
                    item_label=item_label,
                    effective_date=effective_date,
                    path_key=path_key if path_key is not None else self._build_path_key(chapter_label, article_label, paragraph_label, item_label, effective_date),
                    page_number=page_number,
                    location=location,
                    is_addendum=is_addendum,
                    is_appendix=is_appendix,
                )
            )

        def flush_article() -> None:
            nonlocal current_article_lines
            if current_article_label is None or not current_article_lines:
                return
            emit_section(
                source_type=ChunkSourceType.ARTICLE,
                text_lines=current_article_lines,
                location=current_article_label,
                page_number=current_page_number,
                chapter_label=current_chapter,
                article_label=current_article_label,
                path_key=self._build_path_key(current_chapter, current_article_label, None, None),
            )
            current_article_lines = []

        def flush_paragraph() -> None:
            nonlocal current_paragraph_lines
            if current_paragraph_label is None or not current_paragraph_lines:
                return
            emit_section(
                source_type=ChunkSourceType.ARTICLE,
                text_lines=current_paragraph_lines,
                location=self._build_location(current_article_label, current_paragraph_label),
                page_number=current_page_number,
                chapter_label=current_chapter,
                article_label=current_article_label,
                paragraph_label=current_paragraph_label,
                path_key=self._build_path_key(current_chapter, current_article_label, current_paragraph_label, None),
            )
            current_paragraph_lines = []

        def flush_item() -> None:
            nonlocal current_item_label, current_item_lines
            if current_item_label is None or not current_item_lines:
                return
            emit_section(
                source_type=ChunkSourceType.ARTICLE,
                text_lines=current_item_lines,
                location=self._build_location(current_article_label, current_paragraph_label, current_item_label),
                page_number=current_page_number,
                chapter_label=current_chapter,
                article_label=current_article_label,
                paragraph_label=current_paragraph_label,
                item_label=current_item_label,
                path_key=self._build_path_key(current_chapter, current_article_label, current_paragraph_label, current_item_label),
            )
            current_item_lines = []
            current_item_label = None

        def flush_addendum() -> None:
            nonlocal current_addendum_lines
            if not current_addendum_lines:
                return
            addendum_text = self._clean("\n".join(current_addendum_lines))
            effective_date = self._extract_effective_date(addendum_text)
            emit_section(
                source_type=ChunkSourceType.ADDENDUM,
                text_lines=current_addendum_lines,
                location="부칙",
                page_number=current_page_number,
                effective_date=effective_date,
                path_key=("부칙" if effective_date is None else f"부칙>{effective_date}"),
                is_addendum=True,
            )
            current_addendum_lines = []

        def flush_appendix() -> None:
            nonlocal current_appendix_lines, current_appendix_label
            if current_appendix_label is None or not current_appendix_lines:
                return
            emit_section(
                source_type=ChunkSourceType.APPENDIX,
                text_lines=current_appendix_lines,
                location=current_appendix_label,
                page_number=current_page_number,
                path_key=current_appendix_label,
                is_appendix=True,
            )
            current_appendix_lines = []
            current_appendix_label = None

        def reset_article_state() -> None:
            flush_item()
            flush_paragraph()
            flush_article()

        def reset_top_level_state() -> None:
            nonlocal current_article_label, current_paragraph_label, current_item_label
            reset_article_state()
            flush_addendum()
            flush_appendix()
            current_article_label = None
            current_paragraph_label = None
            current_item_label = None

        for section in basic_sections:
            current_page_number = section.page_number
            for raw_line in self._split_lines(section.text):
                line = self._clean(raw_line)
                if not line:
                    continue

                chapter_match = self._CHAPTER_RE.match(line)
                if chapter_match:
                    reset_top_level_state()
                    current_chapter = self._normalize_label(chapter_match.group("label"))
                    continue

                article_match = self._ARTICLE_RE.match(line)
                if article_match:
                    reset_top_level_state()
                    current_article_label = self._normalize_label(article_match.group("label"))
                    current_article_lines = [line]
                    continue

                paragraph_match = self._PARAGRAPH_RE.match(line)
                if paragraph_match and current_article_label is not None:
                    flush_item()
                    flush_paragraph()
                    if current_article_lines:
                        flush_article()
                    current_paragraph_label = self._normalize_label(paragraph_match.group("label"))
                    current_paragraph_lines = [line]
                    continue

                item_label = self._match_item_label(line)
                if item_label and current_article_label is not None:
                    flush_item()
                    if current_paragraph_label is not None:
                        flush_paragraph()
                    elif current_article_lines:
                        flush_article()
                    current_item_label = item_label
                    current_item_lines = [line]
                    continue

                addendum_match = self._ADDENDUM_RE.match(line)
                if addendum_match:
                    reset_top_level_state()
                    current_addendum_lines = [line]
                    continue

                appendix_match = self._APPENDIX_RE.match(line)
                if appendix_match:
                    reset_top_level_state()
                    current_appendix_label = self._normalize_label(appendix_match.group("label"))
                    current_appendix_lines = [line]
                    continue

                if current_item_lines:
                    current_item_lines.append(line)
                elif current_paragraph_lines:
                    current_paragraph_lines.append(line)
                elif current_article_lines:
                    current_article_lines.append(line)
                elif current_addendum_lines:
                    current_addendum_lines.append(line)
                elif current_appendix_lines:
                    current_appendix_lines.append(line)
                else:
                    emit_section(
                        source_type=ChunkSourceType.METADATA,
                        text_lines=[line],
                        location=section.location,
                        page_number=section.page_number,
                        chapter_label=current_chapter,
                        path_key=section.location,
                    )

        reset_top_level_state()

        if not structured_sections:
            raise ValueError("문서에서 구조화할 수 있는 텍스트를 찾지 못했습니다.")
        return structured_sections

    def _clean(self, text: str) -> str:
        text = text.replace("\x00", " ")
        text = re.sub(r"\r\n?", "\n", text)
        text = re.sub(r"[\t\f\v]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    def _looks_like_noise_payload(self, text: str) -> bool:
        compact = re.sub(r"\s+", '', text)
        if not compact:
            return True
        semantic = re.sub(r"[^0-9A-Za-z\uac00-\ud7a3]", '', text)
        if semantic and set(semantic) == {'0'}:
            return True
        if len(semantic) <= 2 and len(compact) <= 12:
            return True
        symbol_chars = re.sub(r"[0-9A-Za-z\uac00-\ud7a3]", '', compact)
        if compact and len(symbol_chars) / len(compact) >= 0.55 and len(semantic) <= 6:
            return True
        if '|' in text and len(semantic) <= 6:
            return True
        return False

    def _is_noise_line(self, text: str) -> bool:
        normalized = self._clean(text)
        if not normalized:
            return True
        if normalized in {'---', '***', '___'}:
            return True
        if re.fullmatch(r"\[\uc2dc\ud589[^\]]*\](?:\s*\[[^\]]*\])?", normalized):
            return True
        if normalized.lower().startswith('title:'):
            return True
        if '|' in normalized and re.sub(r"[|:\-\s]", '', normalized) == '':
            return True
        if self._looks_like_noise_payload(normalized):
            return True
        return False

    def _is_noise_block(self, text: str) -> bool:
        normalized = self._clean(text)
        if not normalized:
            return True
        if re.fullmatch(r"---\s*\ntitle:.*?\n---", normalized, flags=re.IGNORECASE | re.DOTALL):
            return True
        lines = [line for line in (self._clean(part) for part in normalized.splitlines()) if line]
        if not lines:
            return True
        if all(self._is_noise_line(line) for line in lines):
            return True
        return False

    def _split_blocks(self, text: str) -> list[str]:
        return [
            block
            for block in (self._clean(part) for part in re.split(r"\n\s*\n", text))
            if block and not self._is_noise_block(block)
        ]

    def _split_lines(self, text: str) -> list[str]:
        return [
            line
            for line in (self._clean(part) for part in text.splitlines())
            if line and not self._is_noise_line(line)
        ]

    def _build_path_key(
        self,
        chapter_label: str | None,
        article_label: str | None,
        paragraph_label: str | None,
        item_label: str | None,
        effective_date: str | None = None,
    ) -> str:
        parts = [part for part in [chapter_label, article_label, paragraph_label, item_label] if part]
        if effective_date:
            parts.append(effective_date)
        return ">".join(parts)

    def _build_location(
        self,
        article_label: str | None,
        paragraph_label: str | None = None,
        item_label: str | None = None,
    ) -> str:
        parts = [part for part in [article_label, paragraph_label, item_label] if part]
        return " ".join(parts)

    def _normalize_label(self, label: str) -> str:
        return re.sub(r"\s+", "", label).strip()

    def _match_item_label(self, line: str) -> str | None:
        for pattern in self._ITEM_PATTERNS:
            match = pattern.match(line)
            if match:
                return self._normalize_label(match.group("label"))
        return None

    def _extract_effective_date(self, text: str) -> str | None:
        match = self._EFFECTIVE_DATE_RE.search(text)
        if match is None:
            return None
        year = match.group("year")
        month = match.group("month").zfill(2)
        day = match.group("day").zfill(2)
        return f"{year}-{month}-{day}"

    def _parse_pdf(self, file_path: Path) -> list[ParsedSection]:
        sections: list[ParsedSection] = []
        with fitz.open(file_path) as document:
            for index, page in enumerate(document, start=1):
                text = self._clean(page.get_text("text"))
                if text:
                    sections.append(
                        ParsedSection(text=text, location=f"페이지 {index}", page_number=index)
                    )
        return sections

    def _parse_docx(self, file_path: Path) -> list[ParsedSection]:
        from docx import Document

        sections: list[ParsedSection] = []
        document = Document(file_path)
        paragraphs = [self._clean(paragraph.text) for paragraph in document.paragraphs]
        non_empty = [paragraph for paragraph in paragraphs if paragraph]
        for index, paragraph in enumerate(non_empty, start=1):
            sections.append(ParsedSection(text=paragraph, location=f"문단 {index}"))
        return sections

    def _parse_text(self, file_path: Path) -> list[ParsedSection]:
        raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
        sections = self._split_blocks(raw_text)
        return [
            ParsedSection(text=block, location=f"\uad6c\uac04 {index}")
            for index, block in enumerate(sections, start=1)
        ]

    def _parse_hwp_document(self, file_path: Path) -> list[ParsedSection]:
        raw_markdown = self._run_hwp2md(file_path)
        blocks = [self._clean(block) for block in re.split(r"\n\s*\n", raw_markdown)]
        sections = [block for block in blocks if block]
        return [
            ParsedSection(text=block, location=f"구간 {index}")
            for index, block in enumerate(sections, start=1)
        ]

    def _run_hwp2md(self, file_path: Path) -> str:
        binary = self._find_hwp2md_binary()
        if binary is None:
            raise ValueError("HWP/HWPX 변환기(hwp2md)를 찾지 못했습니다.")

        result = subprocess.run(
            [binary, str(file_path)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:
            error_text = self._clean(result.stderr) or "알 수 없는 오류"
            raise ValueError(f"HWP/HWPX 변환에 실패했습니다: {error_text}")

        output = self._clean(result.stdout)
        if not output:
            raise ValueError("HWP/HWPX 문서에서 추출 가능한 텍스트를 찾지 못했습니다.")
        return output

    def _find_hwp2md_binary(self) -> str | None:
        configured_path = os.getenv("HWP2MD_BIN")
        if configured_path:
            return configured_path
        return shutil.which("hwp2md")


