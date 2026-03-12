from app.services.chunker import Chunker
from app.services.document_parser import ParsedSection


def test_chunker_preserves_overlap_and_sequence() -> None:
    section = ParsedSection(text="가" * 1100, location="페이지 1", page_number=1)
    chunker = Chunker(chunk_size=400, chunk_overlap=80)

    chunks = chunker.chunk_sections([section])

    assert len(chunks) >= 3
    assert chunks[0].page_number == 1
    assert chunks[1].chunk_index == 1
    assert len(chunks[0].text) <= 400
