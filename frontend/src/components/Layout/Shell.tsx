import { useEffect, useMemo, useState, type FormEvent, type PropsWithChildren } from 'react';

import { api } from '../../api/client';
import type {
  CategoryDocumentSearchResponse,
  DocumentCategory,
  DocumentRecord,
  HealthResponse,
  LibrarySearchResponse,
  LibraryShortcutScope,
} from '../../types/api';
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
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  const [isCategorySectionOpen, setIsCategorySectionOpen] = useState(false);
  const [categoryQuery, setCategoryQuery] = useState('');
  const [categorySearchLoading, setCategorySearchLoading] = useState(false);
  const [categorySearchResults, setCategorySearchResults] = useState<CategoryDocumentSearchResponse | null>(null);
  const [activeShortcutScope, setActiveShortcutScope] = useState<LibraryShortcutScope | null>(null);
  const [shortcutQuery, setShortcutQuery] = useState('');
  const [shortcutResults, setShortcutResults] = useState<LibrarySearchResponse | null>(null);
  const [shortcutLoading, setShortcutLoading] = useState(false);
  const [shortcutError, setShortcutError] = useState<string | null>(null);

  const categoryCounts = documents.reduce<Record<string, number>>((accumulator, document) => {
    accumulator[document.category] = (accumulator[document.category] ?? 0) + 1;
    return accumulator;
  }, {});

  const documentsByCategory = useMemo(
    () =>
      documents.reduce<Record<string, DocumentRecord[]>>((accumulator, document) => {
        if (!accumulator[document.category]) {
          accumulator[document.category] = [];
        }
        accumulator[document.category].push(document);
        return accumulator;
      }, {}),
    [documents],
  );

  const readyCount = documents.filter((document) => document.status === 'ready').length;
  const processingCount = documents.filter((document) => document.status === 'processing').length;
  const errorCount = documents.filter((document) => document.status === 'error').length;
  const totalCount = Math.max(documents.length, 1);

  const knowledgeStatus = [
    { key: 'ready', label: '상담 가능', value: readyCount, className: 'is-ready' },
    { key: 'processing', label: '색인 중', value: processingCount, className: 'is-processing' },
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

  useEffect(() => {
    if (!expandedCategory) {
      setCategorySearchResults(null);
      setCategorySearchLoading(false);
      return;
    }

    const timeoutId = window.setTimeout(async () => {
      setCategorySearchLoading(true);
      try {
        const response = await api.searchCategoryDocuments({
          category: expandedCategory as DocumentCategory,
          query: categoryQuery,
          limit: 18,
        });
        setCategorySearchResults(response);
      } finally {
        setCategorySearchLoading(false);
      }
    }, 250);

    return () => window.clearTimeout(timeoutId);
  }, [expandedCategory, categoryQuery]);

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
            직원은 근거 문서를 확인하며 질문하고, 운영자는 같은 화면에서 문서를 관리합니다.
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
              <h2 id="shortcut-heading">정책 선반</h2>
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
              <strong className="metric-value">{health?.llm_configured ? '설정됨' : 'API 필요'}</strong>
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

          <section className="sidebar-section compact-sidebar-section sidebar-scroll-section" aria-labelledby="category-heading">
            <div className="section-heading-row">
              <button
                type="button"
                className="sidebar-toggle"
                aria-expanded={isCategorySectionOpen}
                aria-controls="category-section-panel"
                onClick={() => {
                  setIsCategorySectionOpen((current) => !current);
                  if (isCategorySectionOpen) {
                    setExpandedCategory(null);
                    setCategoryQuery('');
                  }
                }}
              >
                <span id="category-heading">문서 구성</span>
                <span className="pill">{isCategorySectionOpen ? 'Hide' : 'Show'}</span>
              </button>
            </div>
            {!isCategorySectionOpen ? (
              <p className="muted-copy small">필요할 때만 펼쳐서 확인하면 됩니다.</p>
            ) : documents.length === 0 ? (
              <p className="muted-copy">아직 등록된 문서가 없습니다.</p>
            ) : (
              <ul id="category-section-panel" className="category-list scroll-chrome-hidden">
                {Object.entries(categoryCounts).map(([category, count]) => (
                  <li key={category} className="category-list-item">
                    <button
                      type="button"
                      className={`category-item ${expandedCategory === category ? 'is-active' : ''}`}
                      onClick={() => {
                        const nextValue = expandedCategory === category ? null : category;
                        setExpandedCategory(nextValue);
                        setCategoryQuery('');
                      }}
                    >
                      <span>{categoryLabels[category as keyof typeof categoryLabels]}</span>
                      <strong>{numberFormatter.format(count)}</strong>
                    </button>
                    {expandedCategory === category ? (
                      <div className="category-documents scroll-chrome-hidden">
                        <input
                          className="text-input category-search-input"
                          value={categoryQuery}
                          placeholder="제목 / 파일명 / 본문 검색"
                          onChange={(event) => setCategoryQuery(event.target.value)}
                        />
                        {categorySearchLoading ? <span className="muted-copy small">검색 중</span> : null}
                        {(categoryQuery.trim() ? categorySearchResults?.results ?? [] : documentsByCategory[category]).map((document) =>
                          'document_id' in document ? (
                            <article
                              key={`${document.document_id}-${document.location}`}
                              className="category-document-card category-document-button"
                              role="button"
                              tabIndex={0}
                              onClick={() => onOpenDocument(document.document_id, document.location, document.snippet)}
                              onKeyDown={(event) => {
                                if (event.key === 'Enter' || event.key === ' ') {
                                  event.preventDefault();
                                  onOpenDocument(document.document_id, document.location, document.snippet);
                                }
                              }}
                            >
                              <strong>{document.title}</strong>
                              <span className="muted-copy small">{document.filename}</span>
                              <span className="muted-copy small">위치: {document.location}</span>
                              <span className="muted-copy small">{document.snippet}</span>
                            </article>
                          ) : (
                            <article key={document.id} className="category-document-card">
                              <strong>{document.title}</strong>
                              <span className="muted-copy small">{document.filename}</span>
                            </article>
                          ),
                        )}
                        {(categoryQuery.trim()
                          ? (categorySearchResults?.results.length ?? 0) === 0 && !categorySearchLoading
                          : documentsByCategory[category].length === 0) ? (
                          <div className="empty-state compact">
                            <strong>검색 결과가 없습니다.</strong>
                            <p className="muted-copy">다른 단어로 다시 찾아보세요.</p>
                          </div>
                        ) : null}
                      </div>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="sidebar-section compact-sidebar-section sidebar-note-section" aria-labelledby="deploy-heading">
            <h2 id="deploy-heading">배포 메모</h2>
            <p className="muted-copy">기능 추가 전에는 운영 정책과 문서 최신 여부를 먼저 확인하세요.</p>
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
              <span className="pill">대상 문서 {shortcutResults?.total_documents ?? 0}건</span>
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
                  <p className="muted-copy">단어를 더 구체적으로 입력하거나 다른 범위를 선택해 보세요.</p>
                </div>
              )}
            </div>
          </section>
        </div>
      ) : null}
    </>
  );
}
