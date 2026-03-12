from fastapi import APIRouter, Depends

from app.dependencies import get_library_search_service
from app.models.schemas import (
    CategoryDocumentSearchRequest,
    CategoryDocumentSearchResponse,
    LibrarySearchRequest,
    LibrarySearchResponse,
)
from app.services.library_search import LibrarySearchService

router = APIRouter(prefix="/api", tags=["library"])


@router.post("/library-search", response_model=LibrarySearchResponse)
def library_search(
    request: LibrarySearchRequest,
    service: LibrarySearchService = Depends(get_library_search_service),
) -> LibrarySearchResponse:
    return service.search(request)


@router.post("/category-search", response_model=CategoryDocumentSearchResponse)
def category_search(
    request: CategoryDocumentSearchRequest,
    service: LibrarySearchService = Depends(get_library_search_service),
) -> CategoryDocumentSearchResponse:
    return service.search_by_category(request)
