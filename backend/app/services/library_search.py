import re
from pathlib import Path

from app.models.schemas import (
    CategoryDocumentSearchRequest,
    CategoryDocumentSearchResponse,
    DocumentStatus,
    LibrarySearchRequest,
    LibrarySearchResponse,
    LibrarySearchResult,
)
from app.services.catalog import DocumentCatalog
from app.services.document_parser import DocumentParser
from app.services.shortcut_scope import ShortcutScopeMatcher


class LibrarySearchService:
    def __init__(
        self,
        catalog: DocumentCatalog,
        parser: DocumentParser,
        scope_matcher: ShortcutScopeMatcher,
    ) -> None:
        self.catalog = catalog
        self.parser = parser
        self.scope_matcher = scope_matcher

    def search(self, request: LibrarySearchRequest) -> LibrarySearchResponse:
        ready_docs = [doc for doc in self.catalog.list_documents() if doc.status == DocumentStatus.READY]
        scoped_docs = [doc for doc in ready_docs if self.scope_matcher.matches(request.scope, doc)]
        return LibrarySearchResponse(
            scope=request.scope,
            query=request.query,
            total_documents=len(scoped_docs),
            results=self._search_documents(scoped_docs, request.query, request.limit),
        )

    def search_by_category(self, request: CategoryDocumentSearchRequest) -> CategoryDocumentSearchResponse:
        ready_docs = [doc for doc in self.catalog.list_documents() if doc.status == DocumentStatus.READY]
        scoped_docs = [doc for doc in ready_docs if doc.category == request.category]
        return CategoryDocumentSearchResponse(
            category=request.category,
            query=request.query,
            total_documents=len(scoped_docs),
            results=self._search_documents(scoped_docs, request.query, request.limit),
        )

    def _search_documents(self, documents, query: str, limit: int) -> list[LibrarySearchResult]:
        if not query.strip():
            return [
                LibrarySearchResult(
                    document_id=doc.id,
                    title=doc.title,
                    filename=doc.filename,
                    category=doc.category,
                    location="문서 안내",
                    snippet=f"{doc.title} 문서를 바로 탐색할 수 있습니다.",
                    score=1.0,
                )
                for doc in documents[:limit]
            ]

        normalized_query = query.strip().lower()
        query_tokens = self._tokens(normalized_query)
        matches: list[LibrarySearchResult] = []

        for doc in documents:
            try:
                sections = self.parser.parse(Path(doc.file_path))
            except Exception:
                continue

            for section in sections:
                score = self._score(doc.title, normalized_query, query_tokens, section.text)
                if score <= 0:
                    continue
                matches.append(
                    LibrarySearchResult(
                        document_id=doc.id,
                        title=doc.title,
                        filename=doc.filename,
                        category=doc.category,
                        location=section.location,
                        snippet=self._snippet(section.text, normalized_query),
                        score=score,
                    )
                )

        matches.sort(key=lambda item: (item.score, item.title), reverse=True)
        return matches[:limit]

    def _tokens(self, query: str) -> list[str]:
        return [token for token in re.split(r"[\s\[\]\(\),./_-]+", query) if len(token) > 1]

    def _score(self, title: str, query: str, tokens: list[str], text: str) -> float:
        title_lower = title.lower()
        text_lower = text.lower()
        score = 0.0
        if query in title_lower:
            score += 10.0
        if query in text_lower:
            score += 25.0
        for token in tokens:
            score += title_lower.count(token) * 5.0
            score += text_lower.count(token) * 2.0
        return score

    def _snippet(self, text: str, query: str, window: int = 180) -> str:
        normalized_text = re.sub(r"\s+", " ", text).strip()
        lower_text = normalized_text.lower()
        index = lower_text.find(query)
        if index == -1:
            return normalized_text[:window]
        start = max(0, index - window // 3)
        end = min(len(normalized_text), index + len(query) + window)
        return normalized_text[start:end].strip()
