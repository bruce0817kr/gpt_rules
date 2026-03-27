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


def test_chunker_keeps_legal_units_on_boundary_when_splitting() -> None:
    section = StructuredSection(
        source_type=ChunkSourceType.ARTICLE,
        text=(
            "제10조(출장비) 출장비는 실제 발생한 비용을 기준으로 한다.\n\n"
            "제1항 교통비는 실비로 지급한다.\n\n"
            "1. 시내 이동은 대중교통을 우선한다.\n\n"
            "2. 시외 이동은 택시비를 포함할 수 있다."
        ),
        article_label="제10조",
        paragraph_label="제1항",
        path_key="제3장>제10조>제1항",
        page_number=3,
        location="제10조 제1항",
    )
    chunker = Chunker(chunk_size=45, chunk_overlap=8)

    parents, children = chunker.chunk_structured_sections(
        document_id="doc-1",
        document_title="Travel Rules",
        sections=[section],
    )

    assert len(parents) == 1
    assert [child.text for child in children] == [
        "제10조(출장비) 출장비는 실제 발생한 비용을 기준으로 한다.",
        "제1항 교통비는 실비로 지급한다.",
        "1. 시내 이동은 대중교통을 우선한다.",
        "2. 시외 이동은 택시비를 포함할 수 있다.",
    ]
    assert parents[0].child_ids == [child.child_id for child in children]
    assert parents[0].representative_text == children[0].text


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


def test_chunker_drops_markdown_rule_and_effective_date_units() -> None:
    section = StructuredSection(
        source_type=ChunkSourceType.ARTICLE,
        text='\u002d\u002d\u002d\n\n[\uc2dc\ud589 2026.1.1.] [2025.12.16., \uc77c\ubd80\uac1c\uc815]\n\n\uc81c10\uc870 \ucd9c\uc7a5\ube44 \uc9c0\uae09 \uae30\uc900\uc740 \ub2e4\uc74c\uacfc \uac19\ub2e4.',
        article_label='\uc81c10\uc870',
        path_key='\uc81c3\uc7a5>\uc81c10\uc870',
        page_number=1,
        location='\uc81c10\uc870',
    )
    chunker = Chunker(chunk_size=200, chunk_overlap=40)

    parents, children = chunker.chunk_structured_sections(
        document_id='doc-1',
        document_title='\uc5ec\ube44 \uaddc\uc815',
        sections=[section],
    )

    assert len(parents) == 1
    assert [child.text for child in children] == ['\uc81c10\uc870 \ucd9c\uc7a5\ube44 \uc9c0\uae09 \uae30\uc900\uc740 \ub2e4\uc74c\uacfc \uac19\ub2e4.']
    assert parents[0].representative_text == '\uc81c10\uc870 \ucd9c\uc7a5\ube44 \uc9c0\uae09 \uae30\uc900\uc740 \ub2e4\uc74c\uacfc \uac19\ub2e4.'



def test_chunker_drops_zero_and_symbol_only_units() -> None:
    section = StructuredSection(
        source_type=ChunkSourceType.ARTICLE,
        text='000000\n\n(?)\n\n| | | | |\n\n\uc81c5\uc870(\uc9d5\uacc4) \uc9d5\uacc4 \uc808\ucc28\ub294 \uc0ac\uc804 \ud1b5\uc9c0\uc640 \uc18c\uba85 \uae30\ud68c\ub97c \ud3ec\ud568\ud55c\ub2e4.',
        article_label='\uc81c5\uc870',
        path_key='\uc81c2\uc7a5>\uc81c5\uc870',
        page_number=1,
        location='\uc81c5\uc870',
    )
    chunker = Chunker(chunk_size=200, chunk_overlap=40)

    parents, children = chunker.chunk_structured_sections(
        document_id='doc-1',
        document_title='\ucde8\uc5c5\uaddc\uce59',
        sections=[section],
    )

    assert len(parents) == 1
    assert [child.text for child in children] == ['\uc81c5\uc870(\uc9d5\uacc4) \uc9d5\uacc4 \uc808\ucc28\ub294 \uc0ac\uc804 \ud1b5\uc9c0\uc640 \uc18c\uba85 \uae30\ud68c\ub97c \ud3ec\ud568\ud55c\ub2e4.']
