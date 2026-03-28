from pathlib import Path

import pytest

from app.models.schemas import ChunkSourceType
from app.services.document_parser import DocumentParser


def test_parse_structured_sections_recognizes_article_addendum_and_appendix(
    tmp_path: Path,
) -> None:
    parser = DocumentParser()
    sample_file = tmp_path / "structured.md"
    sample_file.write_text(
        "# 여비 규정\n\n"
        "제1장 총칙\n\n"
        "제1조(목적) 이 규정은 임직원의 출장비 지급 기준을 정한다.\n\n"
        "제2장 출장\n\n"
        "제10조(출장비) 출장비는 교통비, 숙박비, 식비로 구성한다.\n\n"
        "부칙 <2024. 1. 1.>\n\n"
        "이 규정은 2024년 1월 1일부터 시행한다.\n\n"
        "별표 1 출장비 기준표\n\n"
        "서울 1박 120000원",
        encoding="utf-8",
    )

    sections = parser.parse_structured_sections(sample_file)

    article_sections = [section for section in sections if section.source_type == ChunkSourceType.ARTICLE]
    addendum_sections = [section for section in sections if section.is_addendum]
    appendix_sections = [section for section in sections if section.is_appendix]

    assert len(article_sections) >= 2
    assert article_sections[0].article_label == "제1조"
    assert article_sections[0].chapter_label == "제1장"
    assert article_sections[0].path_key == "제1장>제1조"
    assert article_sections[1].path_key == "제2장>제10조"
    assert addendum_sections and addendum_sections[0].source_type == ChunkSourceType.ADDENDUM
    assert "부칙" in addendum_sections[0].path_key
    assert appendix_sections and appendix_sections[0].source_type == ChunkSourceType.APPENDIX
    assert appendix_sections[0].article_label is None


def test_parse_structured_sections_extracts_paragraph_and_item_hierarchy(
    tmp_path: Path,
) -> None:
    parser = DocumentParser()
    sample_file = tmp_path / "hierarchy.md"
    sample_file.write_text(
        "제1장 총칙\n\n"
        "제1조(목적) 이 규정은 임직원의 출장비 지급 기준을 정한다.\n"
        "제1항 이 규정은 모든 출장에 적용한다.\n"
        "1. 국내 출장의 경우 실제 비용을 기준으로 한다.\n"
        "2. 국외 출장의 경우 별도 기준을 적용한다.\n"
        "제2항 세부 기준은 별표에 따른다.\n\n"
        "부칙 <2024. 1. 1.>\n"
        "이 규정은 2024년 1월 1일부터 시행한다.\n\n"
        "별표 1 출장비 기준표\n"
        "서울 1박 120000원",
        encoding="utf-8",
    )

    sections = parser.parse_structured_sections(sample_file)

    article_sections = [section for section in sections if section.source_type == ChunkSourceType.ARTICLE]
    paragraph_sections = [section for section in sections if section.paragraph_label]
    item_sections = [section for section in sections if section.item_label]

    assert article_sections[0].article_label == "제1조"
    assert article_sections[0].path_key == "제1장>제1조"
    assert paragraph_sections[0].paragraph_label == "제1항"
    assert paragraph_sections[0].path_key == "제1장>제1조>제1항"
    assert item_sections[0].item_label == "1."
    assert item_sections[0].path_key == "제1장>제1조>제1항>1."
    assert item_sections[1].item_label == "2."
    assert item_sections[1].path_key == "제1장>제1조>제1항>2."


def test_parse_structured_sections_preserves_structure_flags_on_legacy_parse_path(
    tmp_path: Path,
) -> None:
    parser = DocumentParser()
    sample_file = tmp_path / "legacy.txt"
    sample_file.write_text("제1조(목적) 첫번째 문단.\n\n두번째 문단.", encoding="utf-8")

    legacy_sections = parser.parse(sample_file)
    structured_sections = parser.parse_structured_sections(sample_file)

    assert legacy_sections[0].text == "제1조(목적) 첫번째 문단."
    assert legacy_sections[1].location == "구간 2"
    assert structured_sections[0].source_type == ChunkSourceType.ARTICLE
    assert structured_sections[0].path_key == "제1조"


def test_parse_hwpx_uses_hwp2md_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    parser = DocumentParser()
    sample_file = tmp_path / "sample.hwpx"
    sample_file.write_text("ignored", encoding="utf-8")

    monkeypatch.setattr(
        parser,
        "_run_hwp2md",
        lambda _: "# ?쒕ぉ\n\n泥?臾몃떒?낅땲??\n\n?섏㎏ 臾몃떒?낅땲??",
    )

    sections = parser.parse(sample_file)

    assert len(sections) == 3
    assert sections[0].text == "# ?쒕ぉ"
    assert sections[1].location == "구간 2"


def test_parse_hwp_raises_when_hwp2md_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    parser = DocumentParser()
    sample_file = tmp_path / "sample.hwp"
    sample_file.write_bytes(b"dummy")

    monkeypatch.setattr(parser, "_find_hwp2md_binary", lambda: None)

    with pytest.raises(ValueError, match="hwp2md"):
        parser.parse(sample_file)


def test_parse_text_ignores_markdown_front_matter_and_rule_lines(tmp_path: Path) -> None:
    parser = DocumentParser()
    sample_file = tmp_path / 'front_matter.md'
    sample_file.write_text(
        '\u002d\u002d\u002d\n'
        'title: \ucde8\uc5c5\uaddc\uce59\n'
        '\u002d\u002d\u002d\n\n'
        '\ucde8\uc5c5\uaddc\uce59\n\n'
        '[\uc2dc\ud589 2026.1.1.] [2025.12.16., \uc77c\ubd80\uac1c\uc815]\n\n'
        '\uc81c1\uc7a5 \ucd1d\uce59\n\n'
        '\uc81c1\uc870(\ubaa9\uc801) \uc774 \uaddc\uce59\uc740 \uc9c1\uc6d0\uc758 \ubcf5\ubb34 \uae30\uc900\uc744 \uc815\ud55c\ub2e4.\n',
        encoding='utf-8',
    )

    sections = parser.parse(sample_file)

    assert [section.text for section in sections] == [
        '\ucde8\uc5c5\uaddc\uce59',
        '\uc81c1\uc7a5 \ucd1d\uce59',
        '\uc81c1\uc870(\ubaa9\uc801) \uc774 \uaddc\uce59\uc740 \uc9c1\uc6d0\uc758 \ubcf5\ubb34 \uae30\uc900\uc744 \uc815\ud55c\ub2e4.',
    ]



def test_parse_text_drops_symbol_and_zero_only_blocks(tmp_path: Path) -> None:
    parser = DocumentParser()
    sample_file = tmp_path / 'noise_blocks.md'
    sample_file.write_text(
        '000000\n\n'
        '| | | | |\n\n'
        '(?)\n\n'
        '\uc81c5\uc870(\uc9d5\uacc4) \uc9d5\uacc4 \uc808\ucc28\ub294 \uc0ac\uc804 \ud1b5\uc9c0\uc640 \uc18c\uba85 \uae30\ud68c\ub97c \ud3ec\ud568\ud55c\ub2e4.\n',
        encoding='utf-8',
    )

    sections = parser.parse(sample_file)

    assert [section.text for section in sections] == ['\uc81c5\uc870(\uc9d5\uacc4) \uc9d5\uacc4 \uc808\ucc28\ub294 \uc0ac\uc804 \ud1b5\uc9c0\uc640 \uc18c\uba85 \uae30\ud68c\ub97c \ud3ec\ud568\ud55c\ub2e4.']
