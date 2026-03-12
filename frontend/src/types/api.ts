export type DocumentCategory = 'foundation' | 'rule' | 'law' | 'guide' | 'notice' | 'other';
export type LibraryShortcutScope = 'hr' | 'finance' | 'general_affairs' | 'general_admin' | 'legal';
export type AnswerMode =
  | 'standard'
  | 'hr_admin'
  | 'contract_review'
  | 'project_management'
  | 'procurement_bid'
  | 'audit_response';
export type FeedbackLabel = 'good' | 'bad';
export type FeedbackReasonCode =
  | 'answer_incorrect'
  | 'grounding_weak'
  | 'citation_mismatch'
  | 'missing_detail'
  | 'format_poor'
  | 'outdated_or_conflict';

export type DocumentStatus = 'processing' | 'ready' | 'error';

export interface DocumentRecord {
  id: string;
  title: string;
  filename: string;
  stored_filename: string;
  file_path: string;
  content_type: string | null;
  category: DocumentCategory;
  category_source: 'auto' | 'manual';
  domain: string;
  tags: string[];
  status: DocumentStatus;
  uploaded_at: string;
  updated_at: string;
  page_count: number;
  chunk_count: number;
  error_message: string | null;
}

export interface Citation {
  index: number;
  document_id: string;
  title: string;
  filename: string;
  category: DocumentCategory;
  location: string;
  page_number: number | null;
  snippet: string;
  score: number;
}

export interface DocumentContentSection {
  location: string;
  page_number: number | null;
  text: string;
}

export interface DocumentContentResponse {
  document_id: string;
  title: string;
  filename: string;
  category: DocumentCategory;
  focus_location: string | null;
  sections: DocumentContentSection[];
}

export interface ChatRequest {
  question: string;
  categories: DocumentCategory[];
  top_k?: number;
  answer_mode?: AnswerMode;
}

export interface ChatResponse {
  response_id: string;
  generated_at: string;
  answer: string;
  citations: Citation[];
  confidence: 'low' | 'medium' | 'high';
  disclaimer: string;
  retrieved_chunks: number;
}

export interface ChatFeedbackRequest {
  response_id: string;
  rating: FeedbackLabel;
  reason_codes?: FeedbackReasonCode[];
}

export interface ChatFeedbackResponse {
  feedback_id: string;
  response_id: string;
  rating: FeedbackLabel;
  reason_codes: FeedbackReasonCode[];
  recorded_at: string;
  superseded_feedback_id: string | null;
}

export const feedbackReasonOptions: Array<{ value: FeedbackReasonCode; label: string }> = [
  { value: 'answer_incorrect', label: '답변 틀림' },
  { value: 'grounding_weak', label: '근거 불량' },
  { value: 'citation_mismatch', label: '인용 불일치' },
  { value: 'missing_detail', label: '핵심 누락' },
  { value: 'format_poor', label: '형식 불편' },
  { value: 'outdated_or_conflict', label: '최신성/충돌' },
];

export const feedbackReasonLabels: Record<FeedbackReasonCode, string> = Object.fromEntries(
  feedbackReasonOptions.map(({ value, label }) => [value, label]),
) as Record<FeedbackReasonCode, string>;

export interface HealthResponse {
  status: string;
  documents: number;
  llm_configured: boolean;
}

export interface LibrarySearchRequest {
  scope: LibraryShortcutScope;
  query: string;
  limit?: number;
}

export interface LibrarySearchResult {
  document_id: string;
  title: string;
  filename: string;
  category: DocumentCategory;
  location: string;
  snippet: string;
  score: number;
}

export interface LibrarySearchResponse {
  scope: LibraryShortcutScope;
  query: string;
  total_documents: number;
  results: LibrarySearchResult[];
}

export interface CategoryDocumentSearchRequest {
  category: DocumentCategory;
  query: string;
  limit?: number;
}

export interface CategoryDocumentSearchResponse {
  category: DocumentCategory;
  query: string;
  total_documents: number;
  results: LibrarySearchResult[];
}

export const categoryOptions: Array<{ value: DocumentCategory; label: string }> = [
  { value: 'foundation', label: '정관/법인 규정' },
  { value: 'rule', label: '내부 규칙' },
  { value: 'law', label: '관련 법령' },
  { value: 'guide', label: '업무 가이드' },
  { value: 'notice', label: '공문/지침' },
  { value: 'other', label: '기타' },
];

export const categoryLabels: Record<DocumentCategory, string> = Object.fromEntries(
  categoryOptions.map(({ value, label }) => [value, label]),
) as Record<DocumentCategory, string>;

export const shortcutLabels: Record<LibraryShortcutScope, string> = {
  hr: '인사 규정',
  finance: '재무 규정',
  general_affairs: '총무 규정',
  general_admin: '일반 행정',
  legal: '관련 법령',
};

export const statusLabels: Record<DocumentStatus, string> = {
  processing: '처리 중',
  ready: '상담 가능',
  error: '오류',
};

export const answerModeOptions: Array<{ value: AnswerMode; label: string }> = [
  { value: 'standard', label: '일반' },
  { value: 'hr_admin', label: '인사담당' },
  { value: 'contract_review', label: '계약 검토' },
  { value: 'project_management', label: '사업관리' },
  { value: 'procurement_bid', label: '구매/입찰' },
  { value: 'audit_response', label: '감사 대응' },
];
