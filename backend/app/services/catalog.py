import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from app.models.schemas import CategorySource, DocumentCategory, DocumentDomain, DocumentRecord, DocumentStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DocumentCatalog:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    stored_filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    content_type TEXT,
                    category TEXT NOT NULL,
                    category_source TEXT NOT NULL DEFAULT 'auto',
                    domain TEXT NOT NULL DEFAULT 'other',
                    source_id TEXT,
                    source_version TEXT,
                    source_url TEXT,
                    content_hash TEXT,
                    tags TEXT NOT NULL,
                    status TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    page_count INTEGER NOT NULL DEFAULT 0,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT
                )
                """
            )
            existing_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(documents)").fetchall()
            }
            if "domain" not in existing_columns:
                connection.execute(
                    "ALTER TABLE documents ADD COLUMN domain TEXT NOT NULL DEFAULT 'other'"
                )
            if "category_source" not in existing_columns:
                connection.execute(
                    "ALTER TABLE documents ADD COLUMN category_source TEXT NOT NULL DEFAULT 'auto'"
                )
            if "source_id" not in existing_columns:
                connection.execute("ALTER TABLE documents ADD COLUMN source_id TEXT")
            if "source_version" not in existing_columns:
                connection.execute("ALTER TABLE documents ADD COLUMN source_version TEXT")
            if "source_url" not in existing_columns:
                connection.execute("ALTER TABLE documents ADD COLUMN source_url TEXT")
            if "content_hash" not in existing_columns:
                connection.execute("ALTER TABLE documents ADD COLUMN content_hash TEXT")
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_documents_updated_at ON documents(updated_at DESC)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_documents_source_identity ON documents(source_id, source_version)"
            )
            connection.commit()

    def _row_to_record(self, row: sqlite3.Row) -> DocumentRecord:
        return DocumentRecord(
            id=row["id"],
            title=row["title"],
            filename=row["filename"],
            stored_filename=row["stored_filename"],
            file_path=row["file_path"],
            content_type=row["content_type"],
            category=DocumentCategory(row["category"]),
            category_source=CategorySource(row["category_source"]),
            domain=DocumentDomain(row["domain"]),
            source_id=row["source_id"],
            source_version=row["source_version"],
            source_url=row["source_url"],
            content_hash=row["content_hash"],
            tags=json.loads(row["tags"]),
            status=DocumentStatus(row["status"]),
            uploaded_at=datetime.fromisoformat(row["uploaded_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            page_count=row["page_count"],
            chunk_count=row["chunk_count"],
            error_message=row["error_message"],
        )

    def list_documents(self) -> list[DocumentRecord]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM documents ORDER BY updated_at DESC, title ASC"
            ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def get_document(self, document_id: str) -> DocumentRecord | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
        return self._row_to_record(row) if row else None

    def find_by_filename(self, filename: str) -> DocumentRecord | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE filename = ? ORDER BY updated_at DESC LIMIT 1",
                (filename,),
            ).fetchone()
        return self._row_to_record(row) if row else None

    def find_by_source_identity(self, source_id: str, source_version: str | None) -> DocumentRecord | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE source_id = ? AND COALESCE(source_version, '') = COALESCE(?, '') ORDER BY updated_at DESC LIMIT 1",
                (source_id, source_version),
            ).fetchone()
        return self._row_to_record(row) if row else None

    def upsert_document(self, record: DocumentRecord) -> DocumentRecord:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    id, title, filename, stored_filename, file_path, content_type,
                    category, category_source, domain, source_id, source_version, source_url, content_hash,
                    tags, status, uploaded_at, updated_at, page_count, chunk_count, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    filename = excluded.filename,
                    stored_filename = excluded.stored_filename,
                    file_path = excluded.file_path,
                    content_type = excluded.content_type,
                    category = excluded.category,
                    category_source = excluded.category_source,
                    domain = excluded.domain,
                    source_id = excluded.source_id,
                    source_version = excluded.source_version,
                    source_url = excluded.source_url,
                    content_hash = excluded.content_hash,
                    tags = excluded.tags,
                    status = excluded.status,
                    uploaded_at = excluded.uploaded_at,
                    updated_at = excluded.updated_at,
                    page_count = excluded.page_count,
                    chunk_count = excluded.chunk_count,
                    error_message = excluded.error_message
                """,
                (
                    record.id,
                    record.title,
                    record.filename,
                    record.stored_filename,
                    record.file_path,
                    record.content_type,
                    record.category.value,
                    record.category_source.value,
                    record.domain.value,
                    record.source_id,
                    record.source_version,
                    record.source_url,
                    record.content_hash,
                    json.dumps(record.tags, ensure_ascii=False),
                    record.status.value,
                    record.uploaded_at.isoformat(),
                    record.updated_at.isoformat(),
                    record.page_count,
                    record.chunk_count,
                    record.error_message,
                ),
            )
            connection.commit()
        return record

    def delete_document(self, document_id: str) -> None:
        with closing(self._connect()) as connection:
            connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            connection.commit()
