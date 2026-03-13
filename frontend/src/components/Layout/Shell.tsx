import { useEffect, useMemo, useState, type FormEvent, type PropsWithChildren } from 'react';

import { api } from '../../api/client';
import { buildLawCollections, formatLawVersion, isLawDocument } from '../../utils/lawCollections';
import type { DocumentRecord, HealthResponse, LibrarySearchResponse, LibraryShortcutScope } from '../../types/api';
import { categoryLabels, shortcutLabels } from '../../types/api';

type ViewMode = 'chat' | 'admin';

interface ShellProps extends PropsWithChildren {
  activeView: ViewMode;
  onViewChange: (view: ViewMode) => void;
  health: HealthResponse | null;
  documents: DocumentRecord[];
  onOpenDocument: (documentId: string, location?: string, snippet?: string) => void;
}

const numberFormatter = new Intl.NumberFormat('ko-KR');

const libraryShortcuts = [
  { code: 'HR', label: '인사 규정', scope: 'hr' as const },
  { code: 'FN', label: '재무 규정', scope: 'finance' as const },
  { code: 'GA', label: '총무 규정', scope: 'general_affairs' as const },
  { code: 'OP', label: '일반 행정', scope: 'general_admin' as const },
  { code: 'LW', label: '관련 법령', scope: 'legal' as const },
];

export function Shell({
  activeView,
  onViewChange,
  health,
  documents,
  children,
  onOpenDocument,
}: ShellProps) {
  const [expandedLawKey, setExpandedLawKey] = useState<string | null>(null);
  const [lawQuery, setLawQuery] = useState('');
  const [activeShortcutScope, setActiveShortcutScope] = useState<LibraryShortcutScope | null>(null);
  const [shortcutQuery, setShortcutQuery] = useState('');
  const [shortcutResults, setShortcutResults] = useState<LibrarySearchResponse | null>(null);
  const [shortcutLoading, setShortcutLoading] = useState(false);
  const [shortcutError, setShortcutError] = useState<string | null>(null);

  const lawCollections = useMemo(() => buildLawCollections(documents), [documents]);
  const filteredLawCollections = useMemo(() => {
    const normalizedQuery = lawQuery.trim().toLocaleLowerCase();
    if (!normalizedQuery) {
      return lawCollections;
    }

    return lawCollections.filter(
      (collection) =>
        collection.title.toLocaleLowerCase().includes(normalizedQuery) ||
        collection.items.some(
          (item) =>
            item.filename.toLocaleLowerCase().includes(normalizedQuery) ||
            item.tags.some((tag) => tag.toLocaleLowerCase().includes(normalizedQuery)),
        ),
    );
  }, [lawCollections, lawQuery]);

  const lawDocumentCount = useMemo(
    () => documents.filter((document) => isLawDocument(document)).length,
    [documents],
  );
  const nonLawDocumentCount = documents.length - lawDocumentCount;

  const readyCount = documents.filter((document) => document.status === 'ready').length;
  const processingCount = documents.filter((document) => document.status === 'processing').length;
  const errorCount = documents.filter((document) => document.status === 'error').length;
  const totalCount = Math.max(documents.length, 1);

  const knowledgeStatus = [
    { key: 'ready', label: '상담 가능', value: readyCount, className: 'is-ready' },
    { key: 'processing', label: '처리 중', value: processingCount, className: 'is-processing' },
    { key: 'error', label: '확인 필요', value: errorCount, className: 'is-error' },
  ];

  const closeShortcutModal = () => {
    setActiveShortcutScope(null);
    setShortcutQuery('');
    setShortcutError(null);
    setShortcutResults(null);
  };

  const runShortcutSearch = async (scope: LibraryShortcutScope, query: string) => {
    setShortcutLoading(true);
    setShortcutError(null);
    try {
      const response = await api.searchLibrary({ scope, query, limit: 14 });
      setShortcutResults(response);
    } catch (error) {
      setShortcutError(error instanceof Error ? error.message : '문서 검색에 실패했습니다.');
    } finally {
      setShortcutLoading(false);
    }
  };

  const openShortcutModal = async (scope: LibraryShortcutScope) => {
    setActiveShortcutScope(scope);
    setShortcutQuery('');
    setShortcutResults(null);
    setShortcutError(null);
    await runShortcutSearch(scope, '');
  };

  useEffect(() => {
    if (!activeShortcutScope) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeShortcutModal();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeShortcutScope]);

  return (
    <>
      <a className="skip-link" href="#app-main">
        본문으로 건너뛰기
      </a>
      <div className="app-shell">
        <aside className="sidebar panel scroll-chrome-hidden">
          <p className="eyebrow">Foundation Operations Console</p>
          <h1 className="brand-title">재단 규정 서재</h1>
          <p className="brand-copy">
            직원은 근거 문서를 확인하고 질문하고, 운영자는 같은 화면에서 문서를 관리합니다.
          </p>

          <nav aria-label="주요 화면" className="view-nav">
            <button
              type="button"
              className={`view-button ${activeView === 'chat' ? 'is-active' : ''}`}
              onClick={() => onViewChange('chat')}
            >
              직원 상담
            </button>
            <button
              type="button"
              className={`view-button ${activeView === 'admin' ? 'is-active' : ''}`}
              onClick={() => onViewChange('admin')}
            >
              문서 관리
            </button>
          </nav>

          <section className="sidebar-section compact-sidebar-section" aria-labelledby="shortcut-heading">
            <div className="section-heading-row">
              <h2 id="shortcut-heading">정책 서랍</h2>
              <span className="pill">빠른 분류</span>
            </div>
            <div className="shortcut-grid">
              {libraryShortcuts.map((shortcut) => (
                <button
                  key={shortcut.code}
                  type="button"
                  className="shortcut-card shortcut-button"
                  onClick={() => void openShortcutModal(shortcut.scope)}
                >
                  <span className="shortcut-code">{shortcut.code}</span>
                  <strong>{shortcut.label}</strong>
                </button>
              ))}
            </div>
          </section>

          <section className="metric-grid compact-metric-grid" aria-label="현황 요약">
            <article className="metric-card">
              <span className="metric-label">문서 수</span>
              <strong className="metric-value">{numberFormatter.format(documents.length)}</strong>
            </article>
            <article className="metric-card">
              <span className="metric-label">LLM 연결</span>
              <strong className="metric-value">{health?.llm_configured ? '정상' : 'API 필요'}</strong>
            </article>
          </section>

          <section className="sidebar-section compact-sidebar-section" aria-labelledby="knowledge-heading">
            <div className="section-heading-row">
              <h2 id="knowledge-heading">Knowledge Status</h2>
              <span className="pill">{numberFormatter.format(documents.length)} docs</span>
            </div>
            <div className="knowledge-list">
              {knowledgeStatus.map((item) => (
                <article key={item.key} className="knowledge-item">
                  <div className="knowledge-header">
                    <span>{item.label}</span>
                    <strong>{numberFormatter.format(item.value)}</strong>
                  </div>
                  <div className="knowledge-track" aria-hidden="true">
                    <span
                      className={`knowledge-fill ${item.className}`}
                      style={{ width: `${(item.value / totalCount) * 100}%` }}
                    />
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="sidebar-section compact-sidebar-section sidebar-scroll-section" aria-labelledby="law-heading">
            <div className="section-heading-row">
              <h2 id="law-heading">법령 구성</h2>
              <span className="pill">법령 {numberFormatter.format(lawCollections.length)}건</span>
            </div>
            {lawCollections.length === 0 ? (
              <div className="empty-state compact">
                <strong>아직 적재된 법령이 없습니다.</strong>
                <p className="muted-copy">문서관리에서 법령명을 입력하면 이 영역에 자동으로 누적됩니다.</p>
              </div>
            ) : (
              <div id="law-section-panel" className="law-section-panel">
                <div className="law-section-summary">
                  <span className="pill is-outline">법령 {numberFormatter.format(lawCollections.length)}건</span>
                  <span className="pill is-outline">법령 문서 {numberFormatter.format(lawDocumentCount)}건</span>
                  <span className="pill is-outline">기타 내부문서 {numberFormatter.format(nonLawDocumentCount)}건</span>
                </div>
                <input
                  className="text-input category-search-input"
                  value={lawQuery}
                  placeholder="법령명 또는 파일명 검색"
                  onChange={(event) => setLawQuery(event.target.value)}
                />
                <ul className="category-list scroll-chrome-hidden">
                  {filteredLawCollections.map((collection) => (
                    <li key={collection.key} className="category-list-item">
                      <button
                        type="button"
                        className={`category-item ${expandedLawKey === collection.key ? 'is-active' : ''}`}
                        onClick={() => setExpandedLawKey((current) => (current === collection.key ? null : collection.key))}
                      >
                        <span>{collection.title}</span>
                        <strong>{numberFormatter.format(collection.documentCount)}</strong>
                      </button>
                      <div className="law-collection-meta">
                        <span className="muted-copy small">
                          {formatLawVersion(collection.latestVersion)
                            ? `시행/버전 ${formatLawVersion(collection.latestVersion)}`
                            : '버전 정보 없음'}
                        </span>
                        {collection.sourceUrl ? (
                          <a className="muted-copy small law-summary-link" href={collection.sourceUrl} target="_blank" rel="noreferrer">
                            원문 보기
                          </a>
                        ) : null}
                      </div>
                      {expandedLawKey === collection.key ? (
                        <div className="category-documents scroll-chrome-hidden">
                          {collection.items.map((document) => (
                            <article
                              key={document.id}
                              className="category-document-card category-document-button"
                              role="button"
                              tabIndex={0}
                              onClick={() => onOpenDocument(document.id)}
                              onKeyDown={(event) => {
                                if (event.key === 'Enter' || event.key === ' ') {
                                  event.preventDefault();
                                  onOpenDocument(document.id);
                                }
                              }}
                            >
                              <strong>{document.title}</strong>
                              <span className="muted-copy small">{document.filename}</span>
                              <span className="muted-copy small">
                                {formatLawVersion(document.source_version)
                                  ? `시행/버전 ${formatLawVersion(document.source_version)}`
                                  : '버전 정보 없음'}
                              </span>
                            </article>
                          ))}
                        </div>
                      ) : null}
                    </li>
                  ))}
                </ul>
                {filteredLawCollections.length === 0 ? (
                  <div className="empty-state compact">
                    <strong>해당 조건의 법령이 없습니다.</strong>
                    <p className="muted-copy">다른 검색어로 다시 확인해 주세요.</p>
                  </div>
                ) : null}
              </div>
            )}
          </section>
        </aside>

        <main id="app-main" className="main-column">
          {children}
        </main>
      </div>

      {activeShortcutScope ? (
        <div className="modal-backdrop" role="presentation" onClick={closeShortcutModal}>
          <section
            className="search-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="shortcut-modal-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div className="modal-title-block">
                <span className="source-label">Library Search</span>
                <h2 id="shortcut-modal-title">{shortcutLabels[activeShortcutScope]} 검색</h2>
              </div>
              <button type="button" className="secondary-button small-button" onClick={closeShortcutModal}>
                닫기
              </button>
            </div>

            <form
              className="modal-search-form"
              onSubmit={(event: FormEvent) => {
                event.preventDefault();
                if (!activeShortcutScope) {
                  return;
                }
                void runShortcutSearch(activeShortcutScope, shortcutQuery);
              }}
            >
              <input
                className="text-input"
                value={shortcutQuery}
                placeholder="예: 복무, 회계, 예산보안, 위원회..."
                onChange={(event) => setShortcutQuery(event.target.value)}
              />
              <button type="submit" className="primary-button" disabled={shortcutLoading}>
                {shortcutLoading ? '검색 중' : '문서 검색'}
              </button>
            </form>

            <div className="modal-meta-row">
              <span className="pill">대상문서 {shortcutResults?.total_documents ?? 0}건</span>
              <span className="inline-hint">선택한 범위 안에서 문서 제목과 본문을 함께 찾습니다.</span>
            </div>

            {shortcutError ? <p className="error-copy">{shortcutError}</p> : null}

            <div className="modal-results scroll-container">
              {shortcutResults && shortcutResults.results.length > 0 ? (
                shortcutResults.results.map((result) => (
                  <article
                    key={`${result.document_id}-${result.location}-${result.score}`}
                    className="modal-result-card category-document-button"
                    role="button"
                    tabIndex={0}
                    onClick={() => onOpenDocument(result.document_id, result.location, result.snippet)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        onOpenDocument(result.document_id, result.location, result.snippet);
                      }
                    }}
                  >
                    <div className="citation-header">
                      <div className="citation-title-block">
                        <span className="source-label">{shortcutLabels[activeShortcutScope]}</span>
                        <strong>{result.title}</strong>
                      </div>
                      <span className="pill">{categoryLabels[result.category]}</span>
                    </div>
                    <div className="citation-chip-row">
                      <span className="doc-chip">문서 {result.filename}</span>
                      <span className="doc-chip">위치 {result.location}</span>
                      <span className="doc-chip">점수 {result.score.toFixed(1)}</span>
                    </div>
                    <p className="citation-snippet">{result.snippet}</p>
                  </article>
                ))
              ) : (
                <div className="empty-state compact">
                  <strong>{shortcutLoading ? '문서를 찾는 중입니다.' : '표시할 결과가 없습니다.'}</strong>
                  <p className="muted-copy">검색어를 더 구체적으로 입력하거나 다른 범위를 선택해 보세요.</p>
                </div>
              )}
            </div>
          </section>
        </div>
      ) : null}
    </>
  );
}
