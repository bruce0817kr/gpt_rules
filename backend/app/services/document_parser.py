import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import fitz
from docx import Document


@dataclass(slots=True)
class ParsedSection:
    text: str
    location: str
    page_number: int | None = None


class DocumentParser:
    supported_suffixes = {".pdf", ".docx", ".txt", ".md", ".hwp", ".hwpx"}

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

    def _clean(self, text: str) -> str:
        text = text.replace("\x00", " ")
        text = re.sub(r"\r\n?", "\n", text)
        text = re.sub(r"[\t\f\v]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

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
        sections: list[ParsedSection] = []
        document = Document(file_path)
        paragraphs = [self._clean(paragraph.text) for paragraph in document.paragraphs]
        non_empty = [paragraph for paragraph in paragraphs if paragraph]
        for index, paragraph in enumerate(non_empty, start=1):
            sections.append(ParsedSection(text=paragraph, location=f"단락 {index}"))
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
