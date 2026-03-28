import { useState, type ChangeEvent, type KeyboardEvent } from 'react';

import {
  answerModeOptions,
  categoryLabels,
  categoryOptions,
  feedbackReasonLabels,
  feedbackReasonOptions,
  type AnswerMode,
  type Citation,
  type DocumentCategory,
  type FeedbackLabel,
  type FeedbackReasonCode,
} from '../../types/api';
import { GUIDEBOOK_TITLE, HERO_BADGES, HERO_TITLE } from '../../content/guidebookContent';

export interface ConversationMessage {
  id: string;
  role: 'assistant' | 'user';
  content: string;
  citations: Citation[];
  confidence?: 'low' | 'medium' | 'high';
  disclaimer?: string;
  responseId?: string;
  generatedAt?: string;
  feedbackRating?: FeedbackLabel;
  feedbackReasons?: FeedbackReasonCode[];
  feedbackRecordedAt?: string;
}

interface ChatPanelProps {
  messages: ConversationMessage[];
  draft: string;
  isSubmitting: boolean;
  errorMessage: string | null;
  selectedCategories: DocumentCategory[];
  answerMode: AnswerMode;
  feedbackSubmittingId: string | null;
  suggestedQuestions: string[];
  onDraftChange: (value: string) => void;
  onToggleCategory: (category: DocumentCategory) => void;
  onAnswerModeChange: (value: AnswerMode) => void;
  onSubmit: () => void;
  onApplySuggestedQuestion: (question: string) => void;
  onOpenCitation: (citation: Citation) => void;
  onSubmitFeedback: (
    messageId: string,
    responseId: string,
    rating: FeedbackLabel,
    reasonCodes: FeedbackReasonCode[],
  ) => void;
}

export function ChatPanel({
  messages,
  draft,
  isSubmitting,
  errorMessage,
  selectedCategories,
  answerMode,
  feedbackSubmittingId,
  suggestedQuestions,
  onDraftChange,
  onToggleCategory,
  onAnswerModeChange,
  onSubmit,
  onApplySuggestedQuestion,
  onOpenCitation,
  onSubmitFeedback,
}: ChatPanelProps) {
  const [feedbackSelections, setFeedbackSelections] = useState<Record<string, FeedbackReasonCode[]>>({});

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((event.metaKey || event.ctrlKey) && event.key === 'Enter' && draft.trim()) {
      event.preventDefault();
      onSubmit();
    }
  };

  const toggleFeedbackReason = (messageId: string, reasonCode: FeedbackReasonCode) => {
    setFeedbackSelections((current) => {
      const selected = current[messageId] ?? [];
      const next = selected.includes(reasonCode)
        ? selected.filter((value) => value !== reasonCode)
        : [...selected, reasonCode];
      return {
        ...current,
        [messageId]: next,
      };
    });
  };

  return (
    <div className="content-stack">
      <section className="panel hero-panel hero-panel-question-first" aria-labelledby="chat-hero-title">
        <p className="eyebrow">{GUIDEBOOK_TITLE}</p>
        <div className="hero-main-block hero-main-block-question-first">
          <div className="hero-badge-row" aria-label="핵심 안내 배지">
            {HERO_BADGES.map((badge) => (
              <span key={badge} className="hero-badge">
                {badge}
              </span>
            ))}
          </div>
          <h2 id="chat-hero-title" className="hero-title">
            {HERO_TITLE}
          </h2>
          <p className="hero-copy">
            내부 규정과 관계 법령을 함께 찾아 근거 중심으로 정리합니다. 추천 질문으로 시작하면 바로 질문 입력창으로 이어집니다.
          </p>
          {suggestedQuestions.length > 0 ? (
            <section className="suggested-question-section" aria-labelledby="suggested-questions-title">
              <div className="section-heading-row compact hero-filter-heading">
                <h2 id="suggested-questions-title">추천 질문</h2>
                <p className="inline-hint">버튼을 누르면 질문을 바로 적용할 수 있습니다.</p>
              </div>
              <div className="suggested-question-list">
                {suggestedQuestions.map((question) => (
                  <button
                    key={question}
                    type="button"
                    className="suggested-question-chip"
                    onClick={() => onApplySuggestedQuestion(question)}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </section>
          ) : null}
        </div>
      </section>

      <section className="panel chat-panel" aria-labelledby="conversation-title">
        <div className="section-heading-row compact">
          <h2 id="conversation-title">상담 기록</h2>
          <div className="status-pill-row" aria-live="polite">
            {isSubmitting ? <span className="pill is-accent">답변 생성 중</span> : null}
            {errorMessage ? <span className="pill is-danger">{errorMessage}</span> : null}
          </div>
        </div>

        <div className="chat-feed" aria-live="polite">
          {messages.map((message) => (
            <article key={message.id} className={`message-card ${message.role}`}>
              <header className="message-header">
                <div className="message-title-block">
                  {message.role === 'assistant' ? <span className="message-kicker">Guidance Card</span> : null}
                  <strong>{message.role === 'assistant' ? '상담 AI' : '직원 질문'}</strong>
                </div>
                <div className="message-pill-row">
                  {message.role === 'assistant' ? <span className="pill is-outline">문서 근거 기반</span> : null}
                  {message.confidence ? <span className="pill">신뢰도 {message.confidence}</span> : null}
                </div>
              </header>
              <p className="message-content">{message.content}</p>

              {message.citations.length > 0 ? (
                <div className="citation-footer">
                  <div className="citation-footer-heading">
                    <span className="message-kicker">Citation</span>
                    <strong>근거 문서</strong>
                  </div>
                  <div className="citation-grid">
                    {message.citations.map((citation) => (
                      <article
                        key={`${message.id}-${citation.index}`}
                        className="citation-card citation-card-button"
                        role="button"
                        tabIndex={0}
                        onClick={() => onOpenCitation(citation)}
                        onKeyDown={(event) => {
                          if (event.key === 'Enter' || event.key === ' ') {
                            event.preventDefault();
                            onOpenCitation(citation);
                          }
                        }}
                      >
                        <div className="citation-header">
                          <div className="citation-title-block">
                            <span className="source-label">Source {citation.index}</span>
                            <strong>{citation.title}</strong>
                          </div>
                          <span className="pill">{categoryLabels[citation.category]}</span>
                        </div>
                        <div className="citation-chip-row">
                          <span className="doc-chip">문서 {citation.filename}</span>
                          <span className="doc-chip">위치 {citation.location}</span>
                          {citation.page_number ? <span className="doc-chip">페이지 {citation.page_number}</span> : null}
                        </div>
                        <p className="citation-meta">근거 강도 {citation.score.toFixed(2)}</p>
                        <p className="citation-snippet">{citation.snippet}</p>
                      </article>
                    ))}
                  </div>
                </div>
              ) : null}

              {message.role === 'assistant' && message.responseId ? (
                <section className="feedback-panel" aria-label="답변 평가">
                  <div className="feedback-heading">
                    <div className="message-title-block">
                      <span className="message-kicker">Quality Check</span>
                      <strong>이번 답변이 충분했나요?</strong>
                      <p className="inline-hint">
                        평가를 남기면 다음 답변의 품질과 선호도가 더 잘 맞도록 조정할 수 있습니다.
                      </p>
                    </div>
                    <div className="message-pill-row">
                      {message.feedbackRecordedAt ? (
                        <span className="pill is-accent">평가 반영됨</span>
                      ) : (
                        <span className="pill">미평가</span>
                      )}
                    </div>
                  </div>
                  <div className="feedback-reason-grid">
                    {feedbackReasonOptions.map((reason) => {
                      const selectedReasons = feedbackSelections[message.id] ?? message.feedbackReasons ?? [];
                      const active = selectedReasons.includes(reason.value);
                      return (
                        <button
                          key={`${message.id}-${reason.value}`}
                          type="button"
                          className={`filter-chip feedback-reason-chip ${active ? 'is-active' : ''}`}
                          aria-pressed={active}
                          onClick={() => toggleFeedbackReason(message.id, reason.value)}
                        >
                          {reason.label}
                        </button>
                      );
                    })}
                  </div>
                  <div className="feedback-actions">
                    <button
                      type="button"
                      className={`secondary-button small-button feedback-button ${
                        message.feedbackRating === 'good' ? 'is-active' : ''
                      }`}
                      disabled={feedbackSubmittingId === message.id}
                      onClick={() =>
                        onSubmitFeedback(
                          message.id,
                          message.responseId!,
                          'good',
                          feedbackSelections[message.id] ?? message.feedbackReasons ?? [],
                        )
                      }
                    >
                      Good
                    </button>
                    <button
                      type="button"
                      className={`secondary-button small-button feedback-button ${
                        message.feedbackRating === 'bad' ? 'is-bad is-active' : 'is-bad'
                      }`}
                      disabled={
                        feedbackSubmittingId === message.id ||
                        (feedbackSelections[message.id] ?? message.feedbackReasons ?? []).length === 0
                      }
                      onClick={() =>
                        onSubmitFeedback(
                          message.id,
                          message.responseId!,
                          'bad',
                          feedbackSelections[message.id] ?? message.feedbackReasons ?? [],
                        )
                      }
                    >
                      Bad
                    </button>
                  </div>
                  <p className="inline-hint">
                    `Bad`에 해당하는 이유 코드를 선택하면 됩니다. 같은 답변을 다시 평가하면 최신 평가가 기준이 됩니다.
                  </p>
                  {message.feedbackReasons && message.feedbackReasons.length > 0 ? (
                    <div className="feedback-chip-row">
                      {message.feedbackReasons.map((reasonCode) => (
                        <span key={`${message.id}-saved-${reasonCode}`} className="pill is-outline">
                          {feedbackReasonLabels[reasonCode]}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </section>
              ) : null}

              {message.disclaimer ? <p className="disclaimer-copy">{message.disclaimer}</p> : null}
            </article>
          ))}
        </div>

        <form
          className="composer composer-question-first"
          onSubmit={(event) => {
            event.preventDefault();
            if (!draft.trim() || isSubmitting) {
              return;
            }
            onSubmit();
          }}
        >
          <label className="field-label" htmlFor="question-input">
            무엇이 궁금한가요?
          </label>
          <textarea
            id="question-input"
            name="question"
            className="text-input text-area"
            placeholder="예: 출장비 지급 기준을 알려주세요."
            value={draft}
            autoComplete="off"
            spellCheck={false}
            onChange={(event: ChangeEvent<HTMLTextAreaElement>) => onDraftChange(event.target.value)}
            onKeyDown={handleKeyDown}
          />
          <div className="composer-footer">
            <p className="inline-hint">규정과 관계 법령을 함께 검토해 근거와 원문 위치를 보여드립니다.</p>
            <button type="submit" className="primary-button composer-cta" disabled={!draft.trim() || isSubmitting}>
              {isSubmitting ? '답변 생성 중' : '근거와 함께 답변 받기'}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
