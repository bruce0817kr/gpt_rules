from pathlib import Path

import pytest

from app.services.document_parser import DocumentParser


def test_parse_hwpx_uses_hwp2md_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    parser = DocumentParser()
    sample_file = tmp_path / "sample.hwpx"
    sample_file.write_text("ignored", encoding="utf-8")

    monkeypatch.setattr(
        parser,
        "_run_hwp2md",
        lambda _: "# 제목\n\n첫 문단입니다.\n\n둘째 문단입니다.",
    )

    sections = parser.parse(sample_file)

    assert len(sections) == 3
    assert sections[0].text == "# 제목"
    assert sections[1].location == "구간 2"


def test_parse_hwp_raises_when_hwp2md_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    parser = DocumentParser()
    sample_file = tmp_path / "sample.hwp"
    sample_file.write_bytes(b"dummy")

    monkeypatch.setattr(parser, "_find_hwp2md_binary", lambda: None)

    with pytest.raises(ValueError, match="hwp2md"):
        parser.parse(sample_file)
