from datetime import datetime, timezone
from pathlib import Path

from app.models.schemas import (
    CategoryDocumentSearchRequest,
    DocumentCategory,
    DocumentDomain,
    DocumentRecord,
    DocumentStatus,
    LibrarySearchRequest,
    LibraryShortcutScope,
)
from app.services.catalog import DocumentCatalog
from app.services.document_parser import DocumentParser
from app.services.library_search import LibrarySearchService
from app.services.shortcut_scope import ShortcutScopeMatcher


def test_library_search_filters_by_scope_and_query(tmp_path: Path) -> None:
    database = tmp_path / 'documents.sqlite3'
    catalog = DocumentCatalog(database)
    now = datetime.now(timezone.utc)

    hr_file = tmp_path / '인사 관리 규정.md'
    hr_file.write_text('인사 발령과 복무 기준을 정한다.', encoding='utf-8')
    finance_file = tmp_path / '재무회계 규정.md'
    finance_file.write_text('예산과 지출 정산 절차를 정한다.', encoding='utf-8')

    catalog.upsert_document(
        DocumentRecord(
            id='hr-doc',
            title='인사 관리 규정',
            filename='인사 관리 규정.md',
            stored_filename='hr.md',
            file_path=str(hr_file),
            category=DocumentCategory.RULE,
            domain=DocumentDomain.OTHER,
            tags=[],
            status=DocumentStatus.READY,
            uploaded_at=now,
            updated_at=now,
        )
    )
    catalog.upsert_document(
        DocumentRecord(
            id='fin-doc',
            title='재무회계 규정',
            filename='재무회계 규정.md',
            stored_filename='fin.md',
            file_path=str(finance_file),
            category=DocumentCategory.RULE,
            domain=DocumentDomain.OTHER,
            tags=[],
            status=DocumentStatus.READY,
            uploaded_at=now,
            updated_at=now,
        )
    )

    service = LibrarySearchService(catalog, DocumentParser(), ShortcutScopeMatcher())
    response = service.search(
        LibrarySearchRequest(scope=LibraryShortcutScope.HR, query='복무', limit=10)
    )

    assert response.total_documents == 1
    assert len(response.results) == 1
    assert response.results[0].document_id == 'hr-doc'


def test_category_search_checks_body_text(tmp_path: Path) -> None:
    database = tmp_path / 'documents.sqlite3'
    catalog = DocumentCatalog(database)
    now = datetime.now(timezone.utc)

    rule_file = tmp_path / '취업규칙.md'
    rule_file.write_text('경조사 휴가의 종류와 일수는 별표에 따라 운영한다.', encoding='utf-8')

    catalog.upsert_document(
        DocumentRecord(
            id='rule-doc',
            title='취업규칙',
            filename='취업규칙.md',
            stored_filename='rule.md',
            file_path=str(rule_file),
            category=DocumentCategory.RULE,
            domain=DocumentDomain.OTHER,
            tags=[],
            status=DocumentStatus.READY,
            uploaded_at=now,
            updated_at=now,
        )
    )

    service = LibrarySearchService(catalog, DocumentParser(), ShortcutScopeMatcher())
    response = service.search_by_category(
        CategoryDocumentSearchRequest(category=DocumentCategory.RULE, query='경조사', limit=10)
    )

    assert response.total_documents == 1
    assert len(response.results) == 1
    assert response.results[0].document_id == 'rule-doc'
