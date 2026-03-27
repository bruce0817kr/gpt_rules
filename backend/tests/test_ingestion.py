from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from app.models.schemas import CategorySource, ChunkSourceType, DocumentCategory, DocumentDomain, DocumentRecord, DocumentStatus, StructuredSection
from app.services.catalog import DocumentCatalog
from app.services.document_parser import ParsedSection
from app.services.ingestion import DocumentIngestionService


def test_index_record_prefers_structured_child_chunks(tmp_path: Path) -> None:
    uploads = tmp_path / 'uploads'
    data = tmp_path / 'data'
    uploads.mkdir()
    data.mkdir()
    file_path = uploads / 'travel.md'
    file_path.write_text('dummy', encoding='utf-8')

    record = DocumentRecord(
        id='doc-1',
        title='여비 규정',
        filename='travel.md',
        stored_filename='travel.md',
        file_path=str(file_path),
        category=DocumentCategory.OTHER,
        category_source=CategorySource.AUTO,
        domain=DocumentDomain.OTHER,
        tags=[],
        status=DocumentStatus.PROCESSING,
        uploaded_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    class FakeParser:
        def parse(self, _path: Path):
            return [ParsedSection(text='제10조 출장비 지급 기준', location='구간 1', page_number=1)]

        def parse_structured_sections(self, _path: Path):
            return [
                StructuredSection(
                    source_type=ChunkSourceType.ARTICLE,
                    text='제10조 출장비 지급 기준은 다음과 같다.',
                    chapter_label='제3장',
                    section_label=None,
                    article_label='제10조',
                    paragraph_label='제1항',
                    item_label=None,
                    effective_date=None,
                    path_key='제3장>제10조>제1항',
                    page_number=1,
                    location='제10조 제1항',
                    is_addendum=False,
                    is_appendix=False,
                )
            ]

    class FakeChunker:
        def __init__(self):
            self.structured_called = False
            self.flat_called = False

        def chunk_sections(self, sections):
            self.flat_called = True
            return [SimpleNamespace(text='fallback', location='구간 1', page_number=1, chunk_index=0)]

        def chunk_structured_sections(self, document_id, document_title, sections):
            self.structured_called = True
            return (
                [
                    SimpleNamespace(
                        parent_id='parent-1',
                        document_id=document_id,
                        document_title=document_title,
                        path_key='제3장>제10조>제1항',
                    )
                ],
                [
                    SimpleNamespace(
                        text='제10조 출장비 지급 기준은 다음과 같다.',
                        location='제10조 제1항',
                        page_number=1,
                        chunk_index=0,
                        child_id='child-1',
                        parent_id='parent-1',
                        path_key='제3장>제10조>제1항',
                        source_type=ChunkSourceType.ARTICLE,
                        is_addendum=False,
                        is_appendix=False,
                    )
                ],
            )

    class FakeClassifier:
        def classify(self, **kwargs):
            return DocumentCategory.RULE

    class FakeVectorStore:
        def __init__(self):
            self.deleted_ids = []
            self.received_chunks = None

        def delete_document(self, document_id: str):
            self.deleted_ids.append(document_id)

        def upsert_document(self, indexed_record, chunks):
            self.received_chunks = chunks
            return len(chunks)

    catalog = DocumentCatalog(data / 'documents.sqlite3')
    catalog.upsert_document(record)
    chunker = FakeChunker()
    vector_store = FakeVectorStore()
    service = DocumentIngestionService(
        settings=SimpleNamespace(upload_dir=uploads, data_dir=data),
        catalog=catalog,
        parser=FakeParser(),
        chunker=chunker,
        category_classifier=FakeClassifier(),
        vector_store=vector_store,
    )

    ready = service._index_record(record)

    assert chunker.structured_called is True
    assert chunker.flat_called is False
    assert vector_store.received_chunks[0].child_id == 'child-1'
    assert vector_store.received_chunks[0].parent_id == 'parent-1'
    assert vector_store.received_chunks[0].path_key == '제3장>제10조>제1항'
    assert ready.category == DocumentCategory.RULE
    assert ready.chunk_count == 1
