import type {
  ChatFeedbackRequest,
  ChatFeedbackResponse,
  ChatRequest,
  ChatResponse,
  CategoryDocumentSearchRequest,
  CategoryDocumentSearchResponse,
  DocumentRecord,
  DocumentContentResponse,
  HealthResponse,
  LibrarySearchRequest,
  LibrarySearchResponse,
} from '../types/api';

const publicBasePath = import.meta.env.BASE_URL.replace(/\/$/, '');
const derivedApiBase = publicBasePath ? `${publicBasePath}/api` : '/api';
const API_BASE =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') || derivedApiBase;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = '요청을 처리하지 못했습니다.';
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export interface UploadDocumentInput {
  file: File;
  title: string;
  category: string;
  tags: string;
}

export const api = {
  health: () => request<HealthResponse>('/health'),
  listDocuments: () => request<DocumentRecord[]>('/documents'),
  askQuestion: (payload: ChatRequest) =>
    request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  submitChatFeedback: (payload: ChatFeedbackRequest) =>
    request<ChatFeedbackResponse>('/chat-feedback', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  searchLibrary: (payload: LibrarySearchRequest) =>
    request<LibrarySearchResponse>('/library-search', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  searchCategoryDocuments: (payload: CategoryDocumentSearchRequest) =>
    request<CategoryDocumentSearchResponse>('/category-search', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  uploadDocument: async (payload: UploadDocumentInput) => {
    const formData = new FormData();
    formData.append('file', payload.file);
    formData.append('title', payload.title);
    formData.append('category', payload.category);
    formData.append('tags', payload.tags);

    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      let message = '문서를 업로드하지 못했습니다.';
      try {
        const body = (await response.json()) as { detail?: string };
        if (body.detail) {
          message = body.detail;
        }
      } catch {
        message = response.statusText || message;
      }
      throw new Error(message);
    }

    return (await response.json()) as DocumentRecord;
  },
  reindexDocument: (documentId: string) =>
    request<DocumentRecord>(`/documents/${documentId}/reindex`, {
      method: 'POST',
    }),
  deleteDocument: (documentId: string) =>
    request<{ deleted: boolean; document_id: string }>(`/documents/${documentId}`, {
      method: 'DELETE',
    }),
  updateDocumentCategory: (documentId: string, category: string) =>
    request<DocumentRecord>(`/documents/${documentId}/category`, {
      method: 'PATCH',
      body: JSON.stringify({ category }),
    }),
  getDocumentContent: (documentId: string, location?: string) =>
    request<DocumentContentResponse>(
      `/documents/${documentId}/content${location ? `?location=${encodeURIComponent(location)}` : ''}`,
    ),
  importLawByName: (lawName: string) =>
    request<DocumentRecord>('/laws/import', {
      method: 'POST',
      body: JSON.stringify({ law_name: lawName }),
    }),
};
