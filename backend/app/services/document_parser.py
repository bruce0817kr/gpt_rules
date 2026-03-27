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

        for section in basic_sections:
            for block in self._split_blocks(section.text):
                if not block:
                    continue
                parsed_section, current_chapter = self._classify_structured_block(
                    block=block,
                    location=section.location,
                    page_number=section.page_number,
                    current_chapter=current_chapter,
                )
                if parsed_section is None:
                    if self._should_append_to_previous(structured_sections):
                        structured_sections[-1].text = self._join_text(structured_sections[-1].text, block)
                    continue
                structured_sections.append(parsed_section)

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

    def _split_blocks(self, text: str) -> list[str]:
        return [block for block in (self._clean(part) for part in re.split(r"\n\s*\n", text)) if block]

    def _join_text(self, first: str, second: str) -> str:
        return f"{first}\n\n{second}".strip()

    def _should_append_to_previous(self, structured_sections: list[StructuredSection]) -> bool:
        if not structured_sections:
            return False
        return structured_sections[-1].source_type in {
            ChunkSourceType.ARTICLE,
            ChunkSourceType.ADDENDUM,
            ChunkSourceType.APPENDIX,
        }

    def _classify_structured_block(
        self,
        block: str,
        location: str,
        page_number: int | None,
        current_chapter: str | None,
    ) -> tuple[StructuredSection | None, str | None]:
        chapter_match = self._CHAPTER_RE.match(block)
        if chapter_match:
            return None, self._normalize_label(chapter_match.group("label"))

        article_match = self._ARTICLE_RE.match(block)
        if article_match:
            article_label = self._normalize_label(article_match.group("label"))
            chapter_label = current_chapter
            title = article_match.group("title")
            text = self._clean(block)
            if title:
                title = self._clean(title)
            path_parts = [part for part in [chapter_label, article_label] if part]
            path_key = ">".join(path_parts) if path_parts else article_label
            return (
                StructuredSection(
                    source_type=ChunkSourceType.ARTICLE,
                    text=text,
                    chapter_label=chapter_label,
                    section_label=None,
                    article_label=article_label,
                    paragraph_label=None,
                    item_label=None,
                    effective_date=None,
                    path_key=path_key,
                    page_number=page_number,
                    location=article_label,
                    is_addendum=False,
                    is_appendix=False,
                ),
                chapter_label,
            )

        addendum_match = self._ADDENDUM_RE.match(block)
        if addendum_match:
            effective_date = self._extract_effective_date(block)
            path_key = "부칙"
            if effective_date:
                path_key = f"{path_key}>{effective_date}"
            return (
                StructuredSection(
                    source_type=ChunkSourceType.ADDENDUM,
                    text=self._clean(block),
                    chapter_label=None,
                    section_label=None,
                    article_label=None,
                    paragraph_label=None,
                    item_label=None,
                    effective_date=effective_date,
                    path_key=path_key,
                    page_number=page_number,
                    location=self._normalize_label(addendum_match.group("label")),
                    is_addendum=True,
                    is_appendix=False,
                ),
                current_chapter,
            )

        appendix_match = self._APPENDIX_RE.match(block)
        if appendix_match:
            label = self._normalize_label(appendix_match.group("label"))
            return (
                StructuredSection(
                    source_type=ChunkSourceType.APPENDIX,
                    text=self._clean(block),
                    chapter_label=None,
                    section_label=None,
                    article_label=None,
                    paragraph_label=None,
                    item_label=None,
                    effective_date=None,
                    path_key=label,
                    page_number=page_number,
                    location=label,
                    is_addendum=False,
                    is_appendix=True,
                ),
                current_chapter,
            )

        metadata_section = StructuredSection(
            source_type=ChunkSourceType.METADATA,
            text=self._clean(block),
            chapter_label=current_chapter,
            section_label=None,
            article_label=None,
            paragraph_label=None,
            item_label=None,
            effective_date=None,
            path_key=location,
            page_number=page_number,
            location=location,
            is_addendum=False,
            is_appendix=False,
        )
        return metadata_section, current_chapter

    def _normalize_label(self, label: str) -> str:
        return re.sub(r"\s+", "", label).strip()

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
        blocks = [self._clean(block) for block in re.split(r"\n\s*\n", raw_text)]
        sections = [block for block in blocks if block]
        return [
            ParsedSection(text=block, location=f"구간 {index}")
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

