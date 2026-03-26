import { useMemo, useState } from 'react';

import { categoryLabels, categoryOptions, statusLabels, type DocumentCategory, type DocumentRecord } from '../../types/api';
import { buildLawCollections, formatLawVersion } from '../../utils/lawCollections';

export interface UploadFormValues {
  files: File[];
  title: string;
  category: DocumentCategory;
  tags: string;
}

interface AdminPanelProps {
  documents: DocumentRecord[];
  isUploading: boolean;
  busyDocumentId: string | null;
  errorMessage: string | null;
  onRefresh: () => Promise<void>;
  onUpload: (values: UploadFormValues) => Promise<void>;
  onDelete: (documentId: string) => Promise<void>;
  onReindex: (documentId: string) => Promise<void>;
  onMoveCategory: (documentId: string, category: DocumentCategory) => Promise<void>;
  onImportLaw: (lawName: string) => Promise<void>;
}

const dateFormatter = new Intl.DateTimeFormat('ko-KR', {
  dateStyle: 'medium',
  timeStyle: 'short',
});

export function AdminPanel({
  documents,
  isUploading,
  busyDocumentId,
  errorMessage,
  onRefresh,
  onUpload,
  onDelete,
  onReindex,
  onMoveCategory,
  onImportLaw,
}: AdminPanelProps) {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState<DocumentCategory>('other');
  const [tags, setTags] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [lawName, setLawName] = useState('');

  const readyCount = useMemo(
    () => documents.filter((document) => document.status === 'ready').length,
    [documents],
  );
  const lawCollections = useMemo(() => buildLawCollections(documents), [documents]);
  const visibleLawCollections = lawCollections.slice(0, 8);

  return (
    <div className="content-stack">
      <section className="panel hero-panel hero-panel-admin" aria-labelledby="admin-title">
        <p className="eyebrow">보조 작업 공간</p>
        <div className="hero-grid hero-grid-admin">
          <div>
            <h2 id="admin-title" className="hero-title">
              문서 관리
            </h2>
            <p className="hero-copy">
              업로드, 재색인, 문서 분류 조정, 법령 수집을 맡는 보조 화면입니다.
            </p>
          </div>
          <div className="hero-callout hero-callout-admin">
            <span className="hero-callout-label">관리 현황</span>
            <ul className="example-list">
              <li>총 문서 {documents.length}건</li>
              <li>상담 가능 {readyCount}건</li>
              <li>처리 오류 {documents.filter((document) => document.status === 'error').length}건</li>
            </ul>
          </div>
        </div>
      </section>

      <div className="admin-workspace">
        <section className="panel upload-panel" aria-labelledby="upload-title">
          <div className="section-heading-row compact">
            <h2 id="upload-title">문서 업로드</h2>
            <div className="status-pill-row" aria-live="polite">
              {isUploading ? <span className="pill is-accent">업로드 중…</span> : null}
              {errorMessage ? <span className="pill is-danger">{errorMessage}</span> : null}
            </div>
          </div>
          <div className="law-import-box">
            <div className="section-heading-row compact">
              <div>
                <h3 className="subsection-title">법령 추가</h3>
                <p className="muted-copy small">국가법령정보 OpenAPI로 필요한 관계 법령 본문을 가져와 적재합니다.</p>
              </div>
            </div>
            <form
              className="law-import-form"
              onSubmit={async (event) => {
                event.preventDefault();
                if (!lawName.trim() || isUploading) {
                  return;
                }
                await onImportLaw(lawName.trim());
                setLawName('');
              }}
            >
              <input
                className="text-input"
                value={lawName}
                placeholder="예: 산업재해보상보험법, 하도급법..."
                onChange={(event) => setLawName(event.target.value)}
              />
              <button type="submit" className="primary-button" disabled={!lawName.trim() || isUploading}>
                법령 추가
              </button>
            </form>
          </div>
          <div className="law-summary-box">
            <div className="section-heading-row compact">
              <div>
                <h3 className="subsection-title">현재 수집된 법령</h3>
                <p className="muted-copy small">이미 적재된 법령을 먼저 확인하고, 없는 경우에만 법령명으로 추가하세요.</p>
              </div>
              <span className="pill">
                법령 {lawCollections.length}건 / 문서 {lawCollections.reduce((sum, item) => sum + item.documentCount, 0)}건
              </span>
            </div>
            {lawCollections.length === 0 ? (
              <div className="empty-state compact">
                <strong>아직 수집된 법령이 없습니다.</strong>
                <p className="muted-copy">법령 추가를 실행하면 여기에 자동으로 누적됩니다.</p>
              </div>
            ) : (
              <>
                <div className="law-summary-list">
                  {visibleLawCollections.map((law) => (
                    <article key={law.key} className="law-summary-card">
                      <div className="law-summary-header">
                        <strong>{law.title}</strong>
                        <span className="pill is-outline">{law.documentCount}건</span>
                      </div>
                      <div className="law-summary-meta">
                        <span className="muted-copy small">
                          {formatLawVersion(law.latestVersion)
                            ? `시행/버전 ${formatLawVersion(law.latestVersion)}`
                            : '버전 정보 없음'}
                        </span>
                        {law.sourceUrl ? (
                          <a
                            className="muted-copy small law-summary-link"
                            href={law.sourceUrl}
                            target="_blank"
                            rel="noreferrer"
                          >
                            원문 보기
                          </a>
                        ) : null}
                      </div>
                    </article>
                  ))}
                </div>
                {lawCollections.length > visibleLawCollections.length ? (
                  <p className="muted-copy small">
                    외 {lawCollections.length - visibleLawCollections.length}건의 법령이 더 등록되어 있습니다.
                  </p>
                ) : null}
              </>
            )}
          </div>
          <form
            className="form-grid upload-form"
            onSubmit={async (event) => {
            event.preventDefault();
            if (files.length === 0 || isUploading) {
              return;
            }
            await onUpload({ files, title, category, tags });
            setTitle('');
            setCategory('other');
            setTags('');
            setFiles([]);
            const fileInput = document.getElementById('document-file') as HTMLInputElement | null;
            if (fileInput) {
              fileInput.value = '';
            }
            }}
          >
            <div className="field-group wide">
              <label className="field-label" htmlFor="document-title">
                문서 제목
              </label>
              <input
                id="document-title"
                name="title"
                className="text-input"
                value={title}
                autoComplete="off"
                placeholder="예: 연구비 집행 세부 규칙…"
                onChange={(event) => setTitle(event.target.value)}
              />
            </div>

            <div className="field-group compact-field-group">
              <label className="field-label" htmlFor="document-category">
                문서 분류
              </label>
              <select
                id="document-category"
                name="category"
                className="text-input"
                value={category}
                onChange={(event) => setCategory(event.target.value as DocumentCategory)}
              >
                {categoryOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <p className="muted-copy small">문서 분류를 지정하지 않으면 제목과 형식을 기준으로 자동 분류합니다.</p>
            </div>

            <div className="field-group compact-field-group">
              <label className="field-label" htmlFor="document-tags">
                태그
              </label>
              <input
                id="document-tags"
                name="tags"
                className="text-input"
                value={tags}
                autoComplete="off"
                placeholder="예: 회계, 집행, 정산…"
                onChange={(event) => setTags(event.target.value)}
              />
            </div>

            <div className="field-group wide">
              <label className="field-label" htmlFor="document-file">
                업로드 파일
              </label>
              <input
                id="document-file"
                name="file"
                className="text-input file-input"
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.md"
                onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
              />
              <p className="muted-copy small">
                여러 파일을 한 번에 올릴 수 있습니다. 여러 파일 선택 시 제목은 파일명 기준으로 자동 처리됩니다.
              </p>
            </div>

            <div className="form-actions wide">
              <button type="submit" className="primary-button" disabled={files.length === 0 || isUploading}>
                {isUploading ? '문서 등록 중…' : `문서 등록${files.length > 1 ? ` (${files.length}건)` : ''}`}
              </button>
              <button type="button" className="secondary-button" onClick={() => void onRefresh()}>
                목록 새로고침
              </button>
            </div>
          </form>
        </section>

        <section className="panel library-panel" aria-labelledby="document-list-title">
          <div className="section-heading-row compact">
            <h2 id="document-list-title">등록 문서</h2>
            <p className="inline-hint">삭제 전에는 반드시 다른 문서와 중복 여부를 확인하세요.</p>
          </div>

          {documents.length === 0 ? (
            <div className="empty-state">
              <strong>아직 등록된 문서가 없습니다.</strong>
              <p className="muted-copy">업로드 후 자동 인덱싱되며, 상담 화면에서 바로 검색됩니다.</p>
            </div>
          ) : (
            <div className="table-wrap table-wrap-scroll">
              <table className="document-table">
                <thead>
                  <tr>
                    <th scope="col">문서</th>
                    <th scope="col">상태</th>
                    <th scope="col">페이지</th>
                    <th scope="col">청크</th>
                    <th scope="col">수정 시각</th>
                    <th scope="col">작업</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((document) => {
                    const busy = busyDocumentId === document.id;
                    return (
                      <tr key={document.id}>
                        <td>
                          <div className="document-cell">
                            <strong>{document.title}</strong>
                            <span className="muted-copy small">{categoryLabels[document.category]}</span>
                            <span className="muted-copy small">
                              {document.category_source === 'manual' ? '수동 분류' : '자동 분류'}
                            </span>
                            {document.category === 'law' || document.source_id ? (
                              <span className="muted-copy small">
                                {formatLawVersion(document.source_version)
                                  ? `법령 버전 ${formatLawVersion(document.source_version)}`
                                  : '법령 문서'}
                              </span>
                            ) : null}
                            <span className="muted-copy small">{document.filename}</span>
                            {document.tags.length > 0 ? (
                              <span className="muted-copy small">태그: {document.tags.join(', ')}</span>
                            ) : null}
                            {document.error_message ? (
                              <span className="error-copy">{document.error_message}</span>
                            ) : null}
                          </div>
                        </td>
                        <td>
                          <div className="document-status-stack">
                            <span className={`pill status-${document.status}`}>{statusLabels[document.status]}</span>
                            <select
                              className="text-input compact-select"
                              value={document.category}
                              onChange={(event) => void onMoveCategory(document.id, event.target.value as DocumentCategory)}
                              disabled={busy}
                            >
                              {categoryOptions.map((option) => (
                                <option key={option.value} value={option.value}>
                                  {option.label}
                                </option>
                              ))}
                            </select>
                          </div>
                        </td>
                        <td className="tabular">{document.page_count}</td>
                        <td className="tabular">{document.chunk_count}</td>
                        <td>{dateFormatter.format(new Date(document.updated_at))}</td>
                        <td>
                          <div className="action-row">
                            <button
                              type="button"
                              className="secondary-button small-button"
                              onClick={() => void onReindex(document.id)}
                              disabled={busy}
                            >
                              {busy ? '처리 중…' : '재색인'}
                            </button>
                            <button
                              type="button"
                              className="secondary-button danger-button small-button"
                              onClick={() => {
                                if (window.confirm(`'${document.title}' 문서를 삭제할까요?`)) {
                                  void onDelete(document.id);
                                }
                              }}
                              disabled={busy}
                            >
                              삭제
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

