from datetime import datetime, timezone
import mimetypes
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import Settings
from app.models.schemas import CategorySource, DocumentCategory, DocumentDomain, DocumentRecord, DocumentStatus
from app.services.catalog import DocumentCatalog
from app.services.category_classifier import DocumentCategoryClassifier
from app.services.chunker import Chunker
from app.services.document_parser import DocumentParser
from app.services.vector_store import QdrantVectorStore


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DocumentIngestionService:
    def __init__(
        self,
        settings: Settings,
        catalog: DocumentCatalog,
        parser: DocumentParser,
        chunker: Chunker,
        category_classifier: DocumentCategoryClassifier,
        vector_store: QdrantVectorStore,
    ) -> None:
        self.settings = settings
        self.catalog = catalog
        self.parser = parser
        self.chunker = chunker
        self.category_classifier = category_classifier
        self.vector_store = vector_store

    async def ingest_upload(
        self,
        upload: UploadFile,
        title: str | None,
        category: DocumentCategory,
        tags: list[str],
    ) -> DocumentRecord:
        filename = upload.filename or "document"
        suffix = Path(filename).suffix.lower()
        if suffix not in self.parser.supported_suffixes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF, DOCX, TXT, MD, HWP, HWPX 파일만 업로드할 수 있습니다.",
            )

        document_id = uuid4().hex
        stored_filename = f"{document_id}{suffix}"
        file_path = self.settings.upload_dir / stored_filename
        with file_path.open("wb") as buffer:
            copyfileobj(upload.file, buffer)

        now = utc_now()
        record = DocumentRecord(
            id=document_id,
            title=title.strip() if title and title.strip() else Path(filename).stem,
            filename=filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            content_type=upload.content_type,
            category=category,
            category_source=CategorySource.MANUAL if category != DocumentCategory.OTHER else CategorySource.AUTO,
            domain=DocumentDomain.OTHER,
            tags=tags,
            status=DocumentStatus.PROCESSING,
            uploaded_at=now,
            updated_at=now,
        )
        self.catalog.upsert_document(record)

        try:
            ready_record = self._index_record(record)
            return ready_record
        except Exception as exc:
            failed_record = record.model_copy(
                update={
                    "status": DocumentStatus.ERROR,
                    "updated_at": utc_now(),
                    "error_message": str(exc),
                }
            )
            self.catalog.upsert_document(failed_record)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"문서 인덱싱에 실패했습니다: {exc}",
            ) from exc

    def reindex_document(self, document_id: str) -> DocumentRecord:
        record = self.catalog.get_document(document_id)
        if record is None:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
        file_path = Path(record.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="원본 파일이 없습니다.")

        processing_record = record.model_copy(
            update={
                "status": DocumentStatus.PROCESSING,
                "updated_at": utc_now(),
                "error_message": None,
            }
        )
        self.catalog.upsert_document(processing_record)

        try:
            self.vector_store.delete_document(document_id)
            return self._index_record(processing_record)
        except Exception as exc:
            failed_record = processing_record.model_copy(
                update={
                    "status": DocumentStatus.ERROR,
                    "updated_at": utc_now(),
                    "error_message": str(exc),
                }
            )
            self.catalog.upsert_document(failed_record)
            raise HTTPException(status_code=500, detail=f"재인덱싱에 실패했습니다: {exc}") from exc

    def delete_document(self, document_id: str) -> None:
        record = self.catalog.get_document(document_id)
        if record is None:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
        self.vector_store.delete_document(document_id)
        file_path = Path(record.file_path)
        if file_path.exists():
            file_path.unlink()
        self.catalog.delete_document(document_id)

    def ingest_saved_file(
        self,
        source_path: Path,
        original_filename: str,
        title: str,
        category: DocumentCategory,
        tags: list[str],
        source_id: str | None = None,
        source_version: str | None = None,
        source_url: str | None = None,
        content_hash: str | None = None,
    ) -> DocumentRecord:
        suffix = source_path.suffix.lower()
        if suffix not in self.parser.supported_suffixes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원하지 않는 파일 형식입니다.",
            )

        document_id = uuid4().hex
        stored_filename = f"{document_id}{suffix}"
        file_path = self.settings.upload_dir / stored_filename
        file_path.write_bytes(source_path.read_bytes())

        now = utc_now()
        record = DocumentRecord(
            id=document_id,
            title=title.strip() if title.strip() else source_path.stem,
            filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            content_type=mimetypes.guess_type(original_filename)[0],
            category=category,
            category_source=CategorySource.MANUAL if category != DocumentCategory.OTHER else CategorySource.AUTO,
            domain=DocumentDomain.OTHER,
            source_id=source_id,
            source_version=source_version,
            source_url=source_url,
            content_hash=content_hash,
            tags=tags,
            status=DocumentStatus.PROCESSING,
            uploaded_at=now,
            updated_at=now,
        )
        self.catalog.upsert_document(record)

        try:
            return self._index_record(record)
        except Exception as exc:
            failed_record = record.model_copy(
                update={
                    "status": DocumentStatus.ERROR,
                    "updated_at": utc_now(),
                    "error_message": str(exc),
                }
            )
            self.catalog.upsert_document(failed_record)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"문서 인덱싱에 실패했습니다: {exc}",
            ) from exc

    def update_document_category(self, document_id: str, category: DocumentCategory) -> DocumentRecord:
        record = self.catalog.get_document(document_id)
        if record is None:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
        file_path = Path(record.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="원본 파일이 없습니다.")

        processing_record = record.model_copy(
            update={
                "category": category,
                "category_source": CategorySource.MANUAL,
                "status": DocumentStatus.PROCESSING,
                "updated_at": utc_now(),
                "error_message": None,
            }
        )
        self.catalog.upsert_document(processing_record)

        try:
            self.vector_store.delete_document(document_id)
            return self._index_record(processing_record)
        except Exception as exc:
            failed_record = processing_record.model_copy(
                update={
                    "status": DocumentStatus.ERROR,
                    "updated_at": utc_now(),
                    "error_message": str(exc),
                }
            )
            self.catalog.upsert_document(failed_record)
            raise HTTPException(status_code=500, detail=f"분류 변경에 실패했습니다: {exc}") from exc

    def _index_record(self, record: DocumentRecord) -> DocumentRecord:
        file_path = Path(record.file_path)
        sections = self.parser.parse(file_path)
        chunks = self.chunker.chunk_sections(sections)
        if not chunks:
            raise ValueError("인덱싱할 텍스트 청크가 없습니다.")

        inferred_category = (
            record.category
            if record.category_source == CategorySource.MANUAL and record.category != DocumentCategory.OTHER
            else self.category_classifier.classify(
                title=record.title,
                filename=record.filename,
                tags=record.tags,
                sections=sections,
            )
        )

        indexed_record = record.model_copy(
            update={
                "category": inferred_category,
                "category_source": record.category_source,
                "domain": DocumentDomain.OTHER,
            }
        )

        self.vector_store.delete_document(record.id)
        chunk_count = self.vector_store.upsert_document(indexed_record, chunks)
        page_count = len({section.page_number for section in sections if section.page_number is not None})
        ready_record = indexed_record.model_copy(
            update={
                "status": DocumentStatus.READY,
                "updated_at": utc_now(),
                "page_count": page_count,
                "chunk_count": chunk_count,
                "error_message": None,
            }
        )
        self.catalog.upsert_document(ready_record)
        return ready_record
