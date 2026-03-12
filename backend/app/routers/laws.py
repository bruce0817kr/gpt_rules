from fastapi import APIRouter, Depends

from app.dependencies import get_law_sync_service
from app.models.schemas import DocumentRecord, LawImportRequest
from app.services.law_sync import LawSyncService

router = APIRouter(prefix="/api/laws", tags=["laws"])


@router.post("/import", response_model=DocumentRecord)
def import_law(
    request: LawImportRequest,
    service: LawSyncService = Depends(get_law_sync_service),
) -> DocumentRecord:
    return service.import_law_by_name(request.law_name)
