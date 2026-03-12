from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.dependencies import get_catalog, get_ingestion_service, get_parser
from app.models.schemas import DocumentCategory, DocumentCategoryUpdateRequest, DocumentContentResponse, DocumentContentSection, DocumentRecord
from app.services.catalog import DocumentCatalog
from app.services.document_parser import DocumentParser
from app.services.ingestion import DocumentIngestionService

router = APIRouter(prefix="/api/documents", tags=["documents"])


def parse_tags(raw_tags: str) -> list[str]:
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


@router.get("", response_model=list[DocumentRecord])
def list_documents(catalog: DocumentCatalog = Depends(get_catalog)) -> list[DocumentRecord]:
    return catalog.list_documents()


@router.get("/{document_id}/content", response_model=DocumentContentResponse)
def get_document_content(
    document_id: str,
    location: str | None = None,
    catalog: DocumentCatalog = Depends(get_catalog),
    parser: DocumentParser = Depends(get_parser),
) -> DocumentContentResponse:
    record = catalog.get_document(document_id)
    if record is None:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    file_path = Path(record.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="원본 파일이 없습니다.")

    sections = parser.parse(file_path)
    return DocumentContentResponse(
        document_id=record.id,
        title=record.title,
        filename=record.filename,
        category=record.category,
        focus_location=location,
        sections=[
            DocumentContentSection(location=section.location, page_number=section.page_number, text=section.text)
            for section in sections
        ],
    )


@router.post("/upload", response_model=DocumentRecord)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    category: DocumentCategory = Form(default=DocumentCategory.OTHER),
    tags: str = Form(default=""),
    ingestion: DocumentIngestionService = Depends(get_ingestion_service),
) -> DocumentRecord:
    return await ingestion.ingest_upload(
        upload=file,
        title=title,
        category=category,
        tags=parse_tags(tags),
    )


@router.post("/{document_id}/reindex", response_model=DocumentRecord)
def reindex_document(
    document_id: str,
    ingestion: DocumentIngestionService = Depends(get_ingestion_service),
) -> DocumentRecord:
    return ingestion.reindex_document(document_id)


@router.patch("/{document_id}/category", response_model=DocumentRecord)
def update_document_category(
    document_id: str,
    request: DocumentCategoryUpdateRequest,
    ingestion: DocumentIngestionService = Depends(get_ingestion_service),
) -> DocumentRecord:
    return ingestion.update_document_category(document_id, request.category)


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    ingestion: DocumentIngestionService = Depends(get_ingestion_service),
) -> dict[str, str | bool]:
    ingestion.delete_document(document_id)
    return {"deleted": True, "document_id": document_id}
