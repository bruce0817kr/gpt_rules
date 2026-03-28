import { useEffect, useState, type FormEvent, type PropsWithChildren } from 'react';

import { api } from '../../api/client';
import { categoryLabels, shortcutLabels } from '../../types/api';
import type {
  Citation,
  DocumentRecord,
  HealthResponse,
  LibrarySearchResponse,
  LibraryShortcutScope,
} from '../../types/api';

type ViewMode = 'chat' | 'admin';

interface ShellProps extends PropsWithChildren {
  activeView: ViewMode;
  onViewChange: (view: ViewMode) => void;
  health: HealthResponse | null;
  documents: DocumentRecord[];
  sessionUsage: {
    questionCount: number;
    responseCount: number;
    citationCount: number;
  };
  latestCitations: Citation[];
  guideTitle: string;
  guideDescription: string;
  onOpenDocument: (documentId: string, location?: string, snippet?: string) => void;
  onOpenLawImport: () => void;
}

const SKIP_LINK_LABEL = '\uBCF8\uBB38\uC73C\uB85C \uAC74\uB108\uB7B5\uAE30';
const CHAT_LABEL = '\uCC44\uD305 \uC548\uB0B4';
const ADMIN_LABEL = '\uBB38\uC11C \uAD00\uB9AC';
const LAW_SHORTCUTS_LABEL = '\uAD00\uACC4 \uBC95\uB839 \uCC3E\uAE30';
const QUICK_SEARCH_LABEL = '\uBE60\uB978 \uAC80\uC0C9';
const LAW_IMPORT_LABEL = '\uBC95\uB839 \uCD94\uAC00';
const RECENT_EVIDENCE_LABEL = '\uCD5C\uADFC \uADFC\uAC70';
const EMPTY_EVIDENCE_TITLE = '\uC544\uC9C1 \uD45C\uC2DC\uD560 \uADFC\uAC70\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4.';
const EMPTY_EVIDENCE_COPY = '\uC9C8\uBB38\uC744 \uBCF4\uB0B4\uBA74 \uCD5C\uC2E0 \uB2F5\uBCC0\uC758 \uADFC\uAC70\uB97C \uC5EC\uAE30\uC5D0 \uBCF4\uC5EC\uC90D\uB2C8\uB2E4.';
const MODAL_TITLE = 'Library Search';
const MODAL_CLOSE_LABEL = '\uB2EB\uAE30';
const SEARCH_PLACEHOLDER = '\uBC95\uB839\uBA85, \uC870\uBB38, \uD0A4\uC6CC\uB4DC\uB85C \uAC80\uC0C9';
const SEARCH_LOADING_LABEL = '\uAC80\uC0C9 \uC911';
const SEARCH_SUBMIT_LABEL = '\uBB38\uC11C \uAC80\uC0C9';
const SEARCH_RESULTS_LABEL = '\uAC80\uC0C9 \uACB0\uACFC';
const SEARCH_RESULTS_HINT = '\uAC80\uC0C9 \uACB0\uACFC\uB97C \uB20C\uB7EC \uC6D0\uBB38 \uC704\uCE58\uC640 \uADFC\uAC70\uB97C \uBC14\uB85C \uC5FD\uB2C8\uB2E4.';
const SEARCH_EMPTY_TITLE = '\uC544\uC9C1 \uD45C\uC2DC\uD560 \uACB0\uACFC\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4.';
const SEARCH_EMPTY_COPY = '\uAC80\uC0C9\uC5B4\uB97C \uB354 \uAD6C\uCCB4\uC801\uC73C\uB85C \uC785\uB825\uD558\uAC70\uB098 \uB2E4\uB978 \uBE60\uB978 \uAC80\uC0C9\uC744 \uC120\uD0DD\uD574 \uBCF4\uC138\uC694.';
const SEARCH_FAILURE_LABEL = '\uBB38\uC11C \uAC80\uC0C9\uC5D0 \uC2E4\uD328\uD588\uC2B5\uB2C8\uB2E4.';
const SEARCH_BUTTON_FALLBACK = '\uBB38\uC11C \uAC80\uC0C9';
const SEARCH_RESULT_PREFIX = '\uAC80\uC0C9 \uACB0\uACFC';
const SOURCE_PREFIX = 'Source';

const lawShortcuts: Array<{ code: string; scope: LibraryShortcutScope }> = [
  { code: 'HR', scope: 'hr' },
  { code: 'FN', scope: 'finance' },
  { code: 'GA', scope: 'general_affairs' },
  { code: 'OP', scope: 'general_admin' },
  { code: 'LW', scope: 'legal' },
];

export function Shell({
  activeView,
  onViewChange,
  health: _health,
  documents: _documents,
  sessionUsage: _sessionUsage,
  latestCitations,
  guideTitle,
  guideDescription,
  children,
  onOpenDocument,
  onOpenLawImport,
}: ShellProps) {
  const [activeShortcutScope, setActiveShortcutScope] = useState<LibraryShortcutScope | null>(null);
  const [shortcutQuery, setShortcutQuery] = useState('');
  const [shortcutResults, setShortcutResults] = useState<LibrarySearchResponse | null>(null);
  const [shortcutLoading, setShortcutLoading] = useState(false);
  const [shortcutError, setShortcutError] = useState<string | null>(null);

  const closeShortcutModal = () => {
    setActiveShortcutScope(null);
    setShortcutQuery('');
    setShortcutResults(null);
    setShortcutError(null);
  };

  const runShortcutSearch = async (scope: LibraryShortcutScope, query: string) => {
    setShortcutLoading(true);
    setShortcutError(null);
    try {
      const response = await api.searchLibrary({ scope, query, limit: 14 });
      setShortcutResults(response);
    } catch (error) {
      setShortcutError(error instanceof Error ? error.message : SEARCH_FAILURE_LABEL);
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
        {SKIP_LINK_LABEL}
      </a>
      <div className="app-shell app-shell-chat-first">
        <main id="app-main" className="main-column">
          {children}
        </main>

        <aside className="support-rail panel" aria-label="\uC9C8\uBB38 \uBCF4\uC870 \uC815\uBCF4">
          <header className="support-rail-header">
            <p className="eyebrow">GTP Guidebook</p>
            <h1 className="brand-title">{guideTitle}</h1>
            <p className="brand-copy">{guideDescription}</p>
          </header>

          <nav className="support-nav" aria-label="\uC8FC\uC694 \uD654\uBA74">
            <button
              type="button"
              className={`view-button ${activeView === 'chat' ? 'is-active' : ''}`}
              onClick={() => onViewChange('chat')}
            >
              {CHAT_LABEL}
            </button>
            <button
              type="button"
              className={`view-button ${activeView === 'admin' ? 'is-active' : ''}`}
              onClick={() => onViewChange('admin')}
            >
              {ADMIN_LABEL}
            </button>
          </nav>

          <section className="support-section" aria-labelledby="law-shortcuts-heading">
            <div className="section-heading-row">
              <h2 id="law-shortcuts-heading">{LAW_SHORTCUTS_LABEL}</h2>
              <span className="pill is-outline">{QUICK_SEARCH_LABEL}</span>
            </div>
            <div className="support-shortcut-grid">
              {lawShortcuts.map((shortcut) => (
                <button
                  key={shortcut.code}
                  type="button"
                  className="support-shortcut-button"
                  onClick={() => void openShortcutModal(shortcut.scope)}
                >
                  <span className="support-shortcut-code">{shortcut.code}</span>
                  <strong>{shortcutLabels[shortcut.scope]}</strong>
                </button>
              ))}
            </div>
            <button type="button" className="secondary-button support-import-button" onClick={onOpenLawImport}>
              {LAW_IMPORT_LABEL}
            </button>
          </section>

          <section className="support-section" aria-labelledby="recent-evidence-heading">
            <div className="section-heading-row">
              <h2 id="recent-evidence-heading">{RECENT_EVIDENCE_LABEL}</h2>
              <span className="pill">{latestCitations.length}건</span>
            </div>
            {latestCitations.length === 0 ? (
              <div className="empty-state compact">
                <strong>{EMPTY_EVIDENCE_TITLE}</strong>
                <p className="muted-copy">{EMPTY_EVIDENCE_COPY}</p>
              </div>
            ) : (
              <div className="recent-evidence-list">
                {latestCitations.map((citation) => (
                  <article
                    key={`latest-${citation.index}-${citation.document_id}`}
                    className="recent-evidence-card citation-card"
                    role="button"
                    tabIndex={0}
                    onClick={() => onOpenDocument(citation.document_id, citation.location, citation.snippet)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        onOpenDocument(citation.document_id, citation.location, citation.snippet);
                      }
                    }}
                  >
                    <div className="citation-header">
                      <div className="citation-title-block">
                        <span className="source-label">{SOURCE_PREFIX} {citation.index}</span>
                        <strong>{citation.title}</strong>
                      </div>
                      <span className="pill">{citation.score.toFixed(2)}</span>
                    </div>
                    <div className="citation-chip-row">
                      <span className="doc-chip">문서 {citation.filename}</span>
                      <span className="doc-chip">범주 {categoryLabels[citation.category]}</span>
                      <span className="doc-chip">위치 {citation.location}</span>
                    </div>
                    <p className="citation-snippet">{citation.snippet}</p>
                  </article>
                ))}
              </div>
            )}
          </section>
        </aside>
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
                <span className="source-label">{MODAL_TITLE}</span>
                <h2 id="shortcut-modal-title">{shortcutLabels[activeShortcutScope]} 검색</h2>
              </div>
              <button type="button" className="secondary-button small-button" onClick={closeShortcutModal}>
                {MODAL_CLOSE_LABEL}
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
                placeholder={SEARCH_PLACEHOLDER}
                onChange={(event) => setShortcutQuery(event.target.value)}
              />
              <button type="submit" className="primary-button" disabled={shortcutLoading}>
                {shortcutLoading ? SEARCH_LOADING_LABEL : SEARCH_SUBMIT_LABEL}
              </button>
            </form>

            <div className="modal-meta-row">
              <span className="pill">
                {SEARCH_RESULTS_LABEL} {shortcutResults?.total_documents ?? 0}건
              </span>
              <span className="inline-hint">{SEARCH_RESULTS_HINT}</span>
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
                  <strong>{shortcutLoading ? SEARCH_LOADING_LABEL : SEARCH_EMPTY_TITLE}</strong>
                  <p className="muted-copy">{SEARCH_EMPTY_COPY}</p>
                </div>
              )}
            </div>
          </section>
        </div>
      ) : null}
    </>
  );
}
