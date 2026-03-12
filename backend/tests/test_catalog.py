from datetime import datetime, timezone

from app.models.schemas import CategorySource, DocumentCategory, DocumentDomain, DocumentRecord, DocumentStatus
from app.services.catalog import DocumentCatalog


def test_catalog_round_trip(tmp_path) -> None:
    catalog = DocumentCatalog(tmp_path / "documents.sqlite3")
    now = datetime.now(timezone.utc)
    record = DocumentRecord(
        id="doc-1",
        title="재단 정관",
        filename="charter.pdf",
        stored_filename="doc-1.pdf",
        file_path=str(tmp_path / "doc-1.pdf"),
        category=DocumentCategory.FOUNDATION,
        category_source=CategorySource.AUTO,
        domain=DocumentDomain.GENERAL_ADMIN,
        tags=["정관", "법인"],
        status=DocumentStatus.READY,
        uploaded_at=now,
        updated_at=now,
        page_count=12,
        chunk_count=32,
    )

    catalog.upsert_document(record)

    stored = catalog.get_document("doc-1")

    assert stored is not None
    assert stored.title == "재단 정관"
    assert stored.category_source == CategorySource.AUTO
    assert stored.domain == DocumentDomain.GENERAL_ADMIN
    assert stored.tags == ["정관", "법인"]
