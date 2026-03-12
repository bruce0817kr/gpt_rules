import { Children, cloneElement, isValidElement, type ReactElement, type ReactNode, useEffect, useRef } from 'react';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { categoryLabels, type DocumentContentResponse } from '../../types/api';

interface SourceViewerDrawerProps {
  document: DocumentContentResponse | null;
  isOpen: boolean;
  onClose: () => void;
  highlightedSnippet?: string | null;
}

export function SourceViewerDrawer({ document, isOpen, onClose, highlightedSnippet }: SourceViewerDrawerProps) {
  const focusRef = useRef<HTMLDivElement | null>(null);

  const highlightChildren = (node: ReactNode): ReactNode => {
    if (!highlightedSnippet) {
      return node;
    }
    if (typeof node === 'string') {
      const snippet = highlightedSnippet.trim();
      if (!snippet) {
        return node;
      }
      const escaped = snippet.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const parts = node.split(new RegExp(`(${escaped})`, 'gi'));
      if (parts.length === 1) {
        return node;
      }
      return parts.map((part, index) =>
        part.toLowerCase() === snippet.toLowerCase() ? <mark key={index}>{part}</mark> : part,
      );
    }
    if (Array.isArray(node)) {
      return Children.map(node, (child) => highlightChildren(child));
    }
    if (isValidElement(node)) {
      const element = node as ReactElement<{ children?: ReactNode }>;
      return cloneElement(element, {
        children: highlightChildren(element.props.children),
      });
    }
    return node;
  };

  useEffect(() => {
    if (isOpen && focusRef.current) {
      focusRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [isOpen, document]);

  if (!isOpen || !document) {
    return null;
  }

  return (
    <div className="drawer-backdrop" role="presentation" onClick={onClose}>
      <aside
        className="source-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="source-drawer-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="drawer-header">
          <div className="drawer-title-block">
            <span className="source-label">Source Viewer</span>
            <h2 id="source-drawer-title">{document.title}</h2>
            <div className="citation-chip-row">
              <span className="doc-chip">문서 {document.filename}</span>
              <span className="doc-chip">분류 {categoryLabels[document.category]}</span>
            </div>
          </div>
          <button type="button" className="secondary-button small-button" onClick={onClose}>
            닫기
          </button>
        </div>

        <div className="drawer-sections scroll-container">
          {document.sections.map((section) => {
            const isFocused = document.focus_location === section.location;
            return (
              <section
                key={`${section.location}-${section.page_number ?? 'na'}`}
                ref={isFocused ? focusRef : null}
                className={`drawer-section ${isFocused ? 'is-focused' : ''}`}
              >
                <div className="citation-header">
                  <div className="citation-title-block">
                    <span className="source-label">{section.location}</span>
                    {section.page_number ? <strong>{section.page_number} page</strong> : null}
                  </div>
                </div>
                <div className="markdown-viewer">
                  {isFocused && highlightedSnippet ? (
                    <div className="drawer-highlight-snippet">
                      <span className="source-label">Cited Snippet</span>
                      <p>{highlightedSnippet}</p>
                    </div>
                  ) : null}
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={
                      isFocused && highlightedSnippet
                        ? {
                            p: ({ children }) => <p>{highlightChildren(children)}</p>,
                            li: ({ children }) => <li>{highlightChildren(children)}</li>,
                            td: ({ children }) => <td>{highlightChildren(children)}</td>,
                            th: ({ children }) => <th>{highlightChildren(children)}</th>,
                          }
                        : undefined
                    }
                  >
                    {section.text}
                  </ReactMarkdown>
                </div>
              </section>
            );
          })}
        </div>
      </aside>
    </div>
  );
}
