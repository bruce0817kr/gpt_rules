from fastapi import APIRouter, Depends

from app.config import get_settings
from app.dependencies import get_catalog
from app.models.schemas import HealthResponse
from app.services.catalog import DocumentCatalog

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(catalog: DocumentCatalog = Depends(get_catalog)) -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        documents=len(catalog.list_documents()),
        llm_configured=bool(settings.openai_api_key),
    )
