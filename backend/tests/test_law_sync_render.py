from app.services.law_sync import LawSyncService


def test_law_markdown_render_contains_header_metadata_and_article_sections(tmp_path) -> None:
    class DummyCatalog:
        def find_by_filename(self, filename):
            return None

    class DummyIngestion:
        pass

    class DummySettings:
        law_oc = "dhl"
        data_dir = tmp_path

    service = LawSyncService(DummySettings(), DummyCatalog(), DummyIngestion())
    payload = {
        "법령": {
            "조문": {
                "조문내용": [
                    ["제1조(목적)", "이 법은 계약의 기본 기준을 정한다."],
                    ["부칙", "이 법은 공포한 날부터 시행한다."],
                    ["별표 1", "입찰 기준표"],
                ]
            }
        }
    }
    item = {
        "법령명한글": "국가를 당사자로 하는 계약에 관한 법률",
        "시행일자": "20251023",
        "공포일자": "20241022",
        "공포번호": "20520",
        "법령일련번호": "265959",
    }

    markdown = service._render_markdown(payload, item)

    assert "# 국가를 당사자로 하는 계약에 관한 법률" in markdown
    assert "- law_name: 국가를 당사자로 하는 계약에 관한 법률" in markdown
    assert "- law_id: " in markdown
    assert "- mst: 265959" in markdown
    assert "### 제1조(목적)" in markdown
    assert "이 법은 계약의 기본 기준을 정한다." in markdown
    assert "### 부칙" in markdown
    assert "### 별표 1" in markdown


def test_law_markdown_render_drops_numeric_and_api_noise(tmp_path) -> None:
    class DummyCatalog:
        def find_by_filename(self, filename):
            return None

    class DummyIngestion:
        pass

    class DummySettings:
        law_oc = "dhl"
        data_dir = tmp_path

    service = LawSyncService(DummySettings(), DummyCatalog(), DummyIngestion())
    payload = {
        "법령": {
            "메타": {
                "API": "https://www.law.go.kr/DRF/lawService.do",
                "참조번호": "000000",
            },
            "조문": {
                "조문내용": [
                    ["제10조", "입찰 공고는 계약의 기본 절차에 따른다."],
                    "000000",
                    "| | | | |",
                    "(인)",
                ]
            },
        }
    }
    item = {
        "법령명한글": "국가를 당사자로 하는 계약에 관한 법률",
        "시행일자": "20251023",
        "공포일자": "20241022",
        "공포번호": "20520",
        "법령일련번호": "265959",
    }

    markdown = service._render_markdown(payload, item)

    assert "000000" not in markdown
    assert "https://www.law.go.kr/DRF/lawService.do" not in markdown
    assert "| | | | |" not in markdown
    assert "(인)" not in markdown
    assert "입찰 공고는 계약의 기본 절차에 따른다." in markdown


def test_law_sync_returns_existing_when_hash_is_unchanged(tmp_path) -> None:
    class DummyExisting:
        content_hash = "same-hash"

    class DummyCatalog:
        def find_by_source_identity(self, source_id, source_version):
            return DummyExisting()

        def find_by_filename(self, filename):
            return None

    class DummyIngestion:
        def delete_document(self, document_id):
            raise AssertionError("should not delete when hash is unchanged")

        def ingest_saved_file(self, **kwargs):
            raise AssertionError("should not ingest when hash is unchanged")

    class DummySettings:
        law_oc = "dhl"
        data_dir = tmp_path

    service = LawSyncService(DummySettings(), DummyCatalog(), DummyIngestion())
    service._search_law = lambda law_name: {
        "법령명한글": "근로기준법",
        "법령일련번호": "265959",
        "시행일자": "20251023",
        "법령ID": "001872",
    }
    service._fetch_law_body = lambda mst, efyd, law_id: {
        "법령": {"조문": {"조문내용": [["제1조(목적)", "내용"]]}}
    }
    service._content_hash = lambda payload: "same-hash"

    result = service.import_law_by_name("근로기준법")

    assert isinstance(result, DummyExisting)


def test_law_sync_passes_enriched_tags_to_ingestion(tmp_path) -> None:
    captured: dict[str, object] = {}

    class DummyCatalog:
        def find_by_source_identity(self, source_id, source_version):
            return None

        def find_by_filename(self, filename):
            return None

    class DummyIngestion:
        def delete_document(self, document_id):
            raise AssertionError("should not delete for fresh import")

        def ingest_saved_file(self, **kwargs):
            captured.update(kwargs)
            return kwargs

    class DummySettings:
        law_oc = "dhl"
        data_dir = tmp_path

    service = LawSyncService(DummySettings(), DummyCatalog(), DummyIngestion())
    service._search_law = lambda law_name: {
        "법령명한글": "근로기준법",
        "법령일련번호": "265959",
        "시행일자": "20251023",
        "법령ID": "001872",
    }
    service._fetch_law_body = lambda mst, efyd, law_id: {
        "법령": {"조문": {"조문내용": [["제1조(목적)", "내용"]]}}
    }
    service.import_law_by_name("근로기준법")

    assert "mst:265959" in captured["tags"]
    assert "effective:20251023" in captured["tags"]
    assert "law-id:001872" in captured["tags"]
    assert any(str(tag).startswith("law-name:") for tag in captured["tags"])
