from dataclasses import dataclass
import re
from typing import Protocol

from app.models.schemas import ChildChunkRecord, ParentChunkRecord, StructuredSection


class _SectionLike(Protocol):
    text: str
    location: str
    page_number: int | None


@dataclass(slots=True)
class Chunk:
    text: str
    location: str
    page_number: int | None
    chunk_index: int


class Chunker:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = min(chunk_overlap, max(chunk_size - 1, 0))

    def chunk_sections(self, sections: list[_SectionLike]) -> list[Chunk]:
        chunks: list[Chunk] = []
        chunk_index = 0
        for section in sections:
            for piece in self._slice(section.text):
                chunks.append(
                    Chunk(
                        text=piece,
                        location=section.location,
                        page_number=section.page_number,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1
        return chunks

    def chunk_structured_sections(
        self,
        document_id: str,
        document_title: str,
        sections: list[StructuredSection],
    ) -> tuple[list[ParentChunkRecord], list[ChildChunkRecord]]:
        parent_records: list[ParentChunkRecord] = []
        child_records: list[ChildChunkRecord] = []
        child_index = 0

        for section_index, section in enumerate(sections):
            pieces = self._slice(section.text)
            if not pieces:
                continue

            parent_id = self._build_parent_id(document_id, section.path_key, section_index)
            child_ids: list[str] = []
            for piece_index, piece in enumerate(pieces):
                child_id = self._build_child_id(parent_id, piece_index)
                child_records.append(
                    ChildChunkRecord(
                        child_id=child_id,
                        parent_id=parent_id,
                        document_id=document_id,
                        document_title=document_title,
                        source_type=section.source_type,
                        path_key=section.path_key,
                        text=piece,
                        page_number=section.page_number,
                        location=section.location,
                        chunk_index=child_index,
                        is_addendum=section.is_addendum,
                        is_appendix=section.is_appendix,
                    )
                )
                child_ids.append(child_id)
                child_index += 1

            parent_records.append(
                ParentChunkRecord(
                    parent_id=parent_id,
                    document_id=document_id,
                    document_title=document_title,
                    source_type=section.source_type,
                    path_key=section.path_key,
                    article_label=section.article_label,
                    text=section.text,
                    representative_text=pieces[0],
                    child_ids=child_ids,
                    page_number=section.page_number,
                    location=section.location,
                    is_addendum=section.is_addendum,
                    is_appendix=section.is_appendix,
                )
            )

        return parent_records, child_records

    def _build_parent_id(self, document_id: str, path_key: str, section_index: int) -> str:
        return f"{document_id}::{path_key}::{section_index}"

    def _build_child_id(self, parent_id: str, child_index: int) -> str:
        return f"{parent_id}::{child_index}"

    def _slice(self, text: str) -> list[str]:
        legal_units = self._split_legal_units(text)
        pieces: list[str] = []
        for unit in legal_units:
            if len(unit) <= self.chunk_size:
                pieces.append(unit)
            else:
                pieces.extend(self._split_long_unit(unit))
        return [piece for piece in pieces if not self._is_weak_text(piece)] or ([] if self._is_weak_text(self._clean(text)) else ([self._clean(text)] if self._clean(text) else []))

    def _split_legal_units(self, text: str) -> list[str]:
        return [unit for unit in (self._clean(part) for part in text.split("\n\n")) if unit and not self._is_weak_text(unit)]

    def _split_long_unit(self, text: str) -> list[str]:
        pieces: list[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(text_length, start + self.chunk_size)
            if end < text_length:
                boundary = self._find_boundary(text, start, end)
                if boundary is not None and boundary > start + max(self.chunk_size // 2, 1):
                    end = boundary
            piece = text[start:end].strip()
            if piece:
                pieces.append(piece)
            if end >= text_length:
                break
            next_start = max(0, end - self.chunk_overlap)
            if next_start <= start:
                next_start = end
            start = next_start
        return pieces

    def _find_boundary(self, text: str, start: int, end: int) -> int | None:
        candidates = [
            text.rfind("\n", start, end),
            text.rfind(". ", start, end),
            text.rfind("? ", start, end),
            text.rfind("! ", start, end),
            text.rfind("; ", start, end),
            text.rfind(" ", start, end),
        ]
        boundary = max(candidates)
        if boundary <= start:
            return None
        return boundary + 1

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

    def _is_weak_text(self, text: str) -> bool:
        normalized = self._clean(text)
        if not normalized:
            return True
        if normalized in {'---', '***', '___'}:
            return True
        if normalized.lower().startswith('title:'):
            return True
        if re.fullmatch(r"\[\uc2dc\ud589[^\]]*\](?:\s*\[[^\]]*\])?", normalized):
            return True
        if '|' in normalized and re.sub(r"[|:\-\s]", '', normalized) == '':
            return True
        if self._looks_like_noise_payload(normalized):
            return True
        return False

    def _clean(self, text: str) -> str:
        return " ".join(text.replace("\r\n", "\n").replace("\r", "\n").split()).strip()
