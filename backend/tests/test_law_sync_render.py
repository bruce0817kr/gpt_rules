from app.services.law_sync import LawSyncService


def test_law_markdown_render_contains_header_metadata(tmp_path) -> None:
    class DummyCatalog:
        def find_by_filename(self, filename):
            return None

    class DummyIngestion:
        pass

    class DummySettings:
        law_oc = 'dhl'
        data_dir = tmp_path

    service = LawSyncService(DummySettings(), DummyCatalog(), DummyIngestion())
    payload = {
        '법령': {
            '조문': {
                '조문내용': [
                    ['제1조 목적', '이 법은 근로조건의 기준을 정한다.'],
                ]
            }
        }
    }
    item = {
        '법령명': '근로기준법',
        '시행일자': '20251023',
        '공포일자': '20241022',
        '공포번호': '20520',
        '법령일련번호': '265959',
    }

    markdown = service._render_markdown(payload, item)

    assert '# 근로기준법' in markdown
    assert '법령일련번호(MST): 265959' in markdown
    assert '제1조 목적' in markdown


def test_law_sync_returns_existing_when_hash_is_unchanged(tmp_path) -> None:
    class DummyExisting:
        content_hash = 'same-hash'

    class DummyCatalog:
        def find_by_source_identity(self, source_id, source_version):
            return DummyExisting()

        def find_by_filename(self, filename):
            return None

    class DummyIngestion:
        def delete_document(self, document_id):
            raise AssertionError('should not delete when hash is unchanged')

        def ingest_saved_file(self, **kwargs):
            raise AssertionError('should not ingest when hash is unchanged')

    class DummySettings:
        law_oc = 'dhl'
        data_dir = tmp_path

    service = LawSyncService(DummySettings(), DummyCatalog(), DummyIngestion())
    service._search_law = lambda law_name: {
        '법령명한글': '근로기준법',
        '법령일련번호': '265959',
        '시행일자': '20251023',
        '법령ID': '001872',
    }
    service._fetch_law_body = lambda mst, efyd, law_id: {'법령': {'조문': {'조문내용': [['제1조 목적', '내용']]}}}
    service._content_hash = lambda markdown: 'same-hash'

    result = service.import_law_by_name('근로기준법')

    assert isinstance(result, DummyExisting)
