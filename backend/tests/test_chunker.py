from dataclasses import dataclass

from app.models.schemas import ChunkSourceType, StructuredSection
from app.services.chunker import Chunker


@dataclass(slots=True)
class SimpleSection:
    text: str
    location: str
    page_number: int | None = None


def test_chunker_preserves_overlap_and_sequence() -> None:
    section = SimpleSection(text="a" * 1100, location="page 1", page_number=1)
    chunker = Chunker(chunk_size=400, chunk_overlap=80)

    chunks = chunker.chunk_sections([section])

    assert len(chunks) >= 3
    assert chunks[0].page_number == 1
    assert chunks[1].chunk_index == 1
    assert len(chunks[0].text) <= 400


def test_chunker_builds_linked_parent_and_child_records() -> None:
    section = StructuredSection(
        source_type=ChunkSourceType.ARTICLE,
        text="Section 10. Travel reimbursement standards are as follows. Paragraph 1. Reimburse actual expenses. Paragraph 2. Set detailed standards separately.",
        article_label="Section 10",
        path_key="Chapter 3>Section 10",
        page_number=3,
        location="Section 10",
    )
    chunker = Chunker(chunk_size=35, chunk_overlap=8)

    parents, children = chunker.chunk_structured_sections(
        document_id="doc-1",
        document_title="Travel Rules",
        sections=[section],
    )

    assert len(parents) == 1
    assert len(children) >= 2
    assert parents[0].child_ids == [child.child_id for child in children]
    assert all(child.parent_id == parents[0].parent_id for child in children)
    assert all(child.document_id == "doc-1" for child in children)
    assert all(child.document_title == "Travel Rules" for child in children)
    assert all(child.source_type == ChunkSourceType.ARTICLE for child in children)
    assert parents[0].representative_text == children[0].text
