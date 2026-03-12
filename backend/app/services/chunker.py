from dataclasses import dataclass

from app.services.document_parser import ParsedSection


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

    def chunk_sections(self, sections: list[ParsedSection]) -> list[Chunk]:
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

    def _slice(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        pieces: list[str] = []
        start = 0
        text_length = len(text)
        while start < text_length:
            end = min(text_length, start + self.chunk_size)
            if end < text_length:
                boundary_candidates = [
                    text.rfind("\n", start, end),
                    text.rfind(". ", start, end),
                    text.rfind("다. ", start, end),
                    text.rfind(" ", start, end),
                ]
                boundary = max(boundary_candidates)
                if boundary > start + self.chunk_size // 2:
                    end = boundary + 1
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
