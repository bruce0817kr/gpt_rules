import { useEffect, useMemo, useState } from 'react';

import { api } from './api/client';
import { AdminPanel, type UploadFormValues } from './components/Admin/AdminPanel';
import { ChatPanel, type ConversationMessage } from './components/Chat/ChatPanel';
import { SourceViewerDrawer } from './components/Chat/SourceViewerDrawer';
import { guideDescription, guideTitle, suggestedQuestions } from './content/guidebookContent';
import { Shell } from './components/Layout/Shell';
import type {
  AnswerMode,
  Citation,
  DocumentCategory,
  DocumentContentResponse,
  DocumentRecord,
  FeedbackLabel,
  FeedbackReasonCode,
  HealthResponse,
} from './types/api';

type ViewMode = 'chat' | 'admin';

function createId(): string {
  return typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function welcomeMessage(): ConversationMessage {
  return {
    id: createId(),
    role: 'assistant',
    content:
      '안녕하세요. 재단 규정, 내부 규칙, 관련 법령을 근거와 함께 찾아드립니다. 질문을 입력하면 관련 문서를 먼저 검색한 뒤 답변과 인용을 함께 보여드립니다.',
    citations: [],
    disclaimer: '최종 결정 전에는 반드시 원문과 최신 개정 여부를 확인하세요.',
  };
}

function readInitialView(): ViewMode {
  const params = new URLSearchParams(window.location.search);
  return params.get('view') === 'admin' ? 'admin' : 'chat';
}

export default function App() {
  const [activeView, setActiveView] = useState<ViewMode>(readInitialView());
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [messages, setMessages] = useState<ConversationMessage[]>([welcomeMessage()]);
  const [draft, setDraft] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<DocumentCategory[]>([]);
  const [answerMode, setAnswerMode] = useState<AnswerMode>('standard');
  const [chatError, setChatError] = useState<string | null>(null);
  const [adminError, setAdminError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackSubmittingId, setFeedbackSubmittingId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [busyDocumentId, setBusyDocumentId] = useState<string | null>(null);
  const [selectedDocumentContent, setSelectedDocumentContent] = useState<DocumentContentResponse | null>(null);
  const [highlightedSnippet, setHighlightedSnippet] = useState<string | null>(null);

  const refreshAll = async () => {
    const [healthData, documentData] = await Promise.all([api.health(), api.listDocuments()]);
    setHealth(healthData);
    setDocuments(documentData);
  };

  useEffect(() => {
    void refreshAll().catch((error: Error) => {
      setAdminError(error.message);
    });
  }, []);

  useEffect(() => {
    const url = new URL(window.location.href);
    url.searchParams.set('view', activeView);
    window.history.replaceState({}, '', `${url.pathname}?${url.searchParams.toString()}`);
  }, [activeView]);

  const latestCitations = useMemo<Citation[]>(() => {
    const latestAssistant = [...messages].reverse().find((message) => message.role === 'assistant');
    return latestAssistant?.citations ?? [];
  }, [messages]);

  const sessionUsage = useMemo(() => {
    const questionCount = messages.filter((message) => message.role === 'user').length;
    const responseMessages = messages.filter((message) => message.role === 'assistant' && message.responseId);
    const responseCount = responseMessages.length;
    const citationCount = responseMessages.reduce((total, message) => total + message.citations.length, 0);

    return {
      questionCount,
      responseCount,
      citationCount,
    };
  }, [messages]);

  const submitQuestion = async () => {
    const question = draft.trim();
    if (!question) {
      return;
    }

    setChatError(null);
    setIsSubmitting(true);

    const userMessage: ConversationMessage = {
      id: createId(),
      role: 'user',
      content: question,
      citations: [],
    };
    setMessages((current) => [...current, userMessage]);
    setDraft('');

    try {
      const response = await api.askQuestion({
        question,
        categories: selectedCategories,
        answer_mode: answerMode,
      });
      const assistantMessage: ConversationMessage = {
        id: createId(),
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
        confidence: response.confidence,
        disclaimer: response.disclaimer,
        responseId: response.response_id,
        generatedAt: response.generated_at,
      };
      setMessages((current) => [...current, assistantMessage]);
      await refreshAll();
    } catch (error) {
      const message = error instanceof Error ? error.message : '질문을 처리하지 못했습니다.';
      setChatError(message);
      setMessages((current) => [
        ...current,
        {
          id: createId(),
          role: 'assistant',
          content: '답변 생성 중 오류가 발생했습니다. 잠시 후 다시 시도하거나 문서 관리 화면에서 색인 상태를 확인해 주세요.',
          citations: [],
          disclaimer: message,
        },
      ]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitMessageFeedback = async (
    messageId: string,
    responseId: string,
    rating: FeedbackLabel,
    reasonCodes: FeedbackReasonCode[],
  ) => {
    setChatError(null);
    setFeedbackSubmittingId(messageId);
    try {
      const response = await api.submitChatFeedback({
        response_id: responseId,
        rating,
        reason_codes: reasonCodes,
      });
      setMessages((current) =>
        current.map((message) =>
          message.id === messageId
            ? {
                ...message,
                feedbackRating: response.rating,
                feedbackReasons: response.reason_codes,
                feedbackRecordedAt: response.recorded_at,
              }
            : message,
        ),
      );
    } catch (error) {
      setChatError(error instanceof Error ? error.message : '답변 평가를 저장하지 못했습니다.');
    } finally {
      setFeedbackSubmittingId(null);
    }
  };

  const toggleCategory = (category: DocumentCategory) => {
    setSelectedCategories((current) =>
      current.includes(category) ? current.filter((value) => value !== category) : [...current, category],
    );
  };

  const uploadDocument = async (values: UploadFormValues) => {
    setAdminError(null);
    setIsUploading(true);
    try {
      for (const [index, file] of values.files.entries()) {
        await api.uploadDocument({
          file,
          title: values.files.length === 1 ? values.title : '',
          category: values.category,
          tags: values.tags,
        });
        if (index % 5 === 0) {
          await refreshAll();
        }
      }
      await refreshAll();
      setActiveView('admin');
    } catch (error) {
      setAdminError(error instanceof Error ? error.message : '문서 업로드에 실패했습니다.');
    } finally {
      setIsUploading(false);
    }
  };

  const reindexDocument = async (documentId: string) => {
    setAdminError(null);
    setBusyDocumentId(documentId);
    try {
      await api.reindexDocument(documentId);
      await refreshAll();
    } catch (error) {
      setAdminError(error instanceof Error ? error.message : '재색인에 실패했습니다.');
    } finally {
      setBusyDocumentId(null);
    }
  };

  const deleteDocument = async (documentId: string) => {
    setAdminError(null);
    setBusyDocumentId(documentId);
    try {
      await api.deleteDocument(documentId);
      await refreshAll();
    } catch (error) {
      setAdminError(error instanceof Error ? error.message : '문서 삭제에 실패했습니다.');
    } finally {
      setBusyDocumentId(null);
    }
  };

  const moveDocumentCategory = async (documentId: string, category: DocumentCategory) => {
    setAdminError(null);
    setBusyDocumentId(documentId);
    try {
      await api.updateDocumentCategory(documentId, category);
      await refreshAll();
    } catch (error) {
      setAdminError(error instanceof Error ? error.message : '문서 분류 변경에 실패했습니다.');
    } finally {
      setBusyDocumentId(null);
    }
  };

  const importLaw = async (lawName: string) => {
    setAdminError(null);
    setIsUploading(true);
    try {
      await api.importLawByName(lawName);
      await refreshAll();
      setActiveView('admin');
    } catch (error) {
      setAdminError(error instanceof Error ? error.message : '법령 추가에 실패했습니다.');
    } finally {
      setIsUploading(false);
    }
  };

  const openCitation = async (citation: Citation) => {
    try {
      const content = await api.getDocumentContent(citation.document_id, citation.location);
      setSelectedDocumentContent(content);
      setHighlightedSnippet(citation.snippet);
    } catch (error) {
      setChatError(error instanceof Error ? error.message : '근거 문서를 불러오지 못했습니다.');
    }
  };

  const handleOpenLawImport = () => {
    setActiveView('admin');
  };

  const applySuggestedQuestion = (question: string) => {
    setDraft(question);
  };

  const shellExtras = {
    guideTitle,
    guideDescription,
    latestCitations,
    onOpenLawImport: handleOpenLawImport,
  };

  const chatPanelExtras = {
    suggestedQuestions,
    onApplySuggestedQuestion: applySuggestedQuestion,
  };

  return (
    <Shell
      {...(shellExtras as any)}
      activeView={activeView}
      onViewChange={setActiveView}
      health={health}
      documents={documents}
      sessionUsage={sessionUsage}
      onOpenDocument={(documentId, location, snippet) => {
        void (async () => {
          try {
            const content = await api.getDocumentContent(documentId, location);
            setSelectedDocumentContent(content);
            setHighlightedSnippet(snippet ?? null);
          } catch (error) {
            setChatError(error instanceof Error ? error.message : '근거 문서를 불러오지 못했습니다.');
          }
        })();
      }}
    >
      {activeView === 'chat' ? (
        <ChatPanel
          {...(chatPanelExtras as any)}
          messages={messages}
          draft={draft}
          isSubmitting={isSubmitting}
          errorMessage={chatError}
          selectedCategories={selectedCategories}
          answerMode={answerMode}
          feedbackSubmittingId={feedbackSubmittingId}
          onDraftChange={setDraft}
          onToggleCategory={toggleCategory}
          onAnswerModeChange={setAnswerMode}
          onSubmit={() => void submitQuestion()}
          onOpenCitation={openCitation}
          onSubmitFeedback={(messageId, responseId, rating, reasonCodes) =>
            void submitMessageFeedback(messageId, responseId, rating, reasonCodes)
          }
        />
      ) : (
        <AdminPanel
          documents={documents}
          isUploading={isUploading}
          busyDocumentId={busyDocumentId}
          errorMessage={adminError}
          onRefresh={refreshAll}
          onUpload={uploadDocument}
          onDelete={deleteDocument}
          onReindex={reindexDocument}
          onMoveCategory={moveDocumentCategory}
          onImportLaw={importLaw}
        />
      )}

      {activeView === 'chat' ? (
        <section className="panel evidence-panel" aria-labelledby="evidence-title">
          <div className="section-heading-row compact">
            <h2 id="evidence-title">최근 근거 묶음</h2>
            <span className="pill">{latestCitations.length}개 인용</span>
          </div>
          {latestCitations.length === 0 ? (
            <div className="empty-state compact">
              <strong>아직 표시할 인용이 없습니다.</strong>
              <p className="muted-copy">질문을 보내면 최신 답변의 근거 조항을 여기에 함께 보여드립니다.</p>
            </div>
          ) : (
            <div className="citation-grid">
              {latestCitations.map((citation) => (
                <article
                  key={`latest-${citation.index}-${citation.document_id}`}
                  className="citation-card citation-card-button"
                  role="button"
                  tabIndex={0}
                  onClick={() => void openCitation(citation)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault();
                      void openCitation(citation);
                    }
                  }}
                >
                  <div className="citation-header">
                    <div className="citation-title-block">
                      <span className="source-label">Source {citation.index}</span>
                      <strong>{citation.title}</strong>
                    </div>
                    <span className="pill">근거 {citation.score.toFixed(2)}</span>
                  </div>
                  <div className="citation-chip-row">
                    <span className="doc-chip">문서 {citation.filename}</span>
                    <span className="doc-chip">분류 {citation.category}</span>
                    <span className="doc-chip">
                      위치 {citation.location}
                      {citation.page_number ? ` / ${citation.page_number}p` : ''}
                    </span>
                  </div>
                  <p className="citation-meta">최신 답변에서 직접 인용한 조항 요약</p>
                  <p className="citation-snippet">{citation.snippet}</p>
                </article>
              ))}
            </div>
          )}
        </section>
      ) : null}

      <SourceViewerDrawer
        document={selectedDocumentContent}
        isOpen={selectedDocumentContent !== null}
        onClose={() => {
          setSelectedDocumentContent(null);
          setHighlightedSnippet(null);
        }}
        highlightedSnippet={highlightedSnippet}
      />
    </Shell>
  );
}
