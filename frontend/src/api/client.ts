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

function normalizeApiBase(value: string | undefined | null): string | null {
  if (!value) {
    return null;
  }

  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }

  return trimmed.replace(/\/$/, '');
}

function pushCandidate(target: string[], value: string | null): void {
  if (!value || target.includes(value)) {
    return;
  }

  target.push(value);
}

const publicBasePath = import.meta.env.BASE_URL.replace(/\/$/, '');
const explicitApiBase = normalizeApiBase(import.meta.env.VITE_API_URL as string | undefined);
const derivedApiBase = publicBasePath ? `${publicBasePath}/api` : '/api';

function buildApiBaseCandidates(): string[] {
  const candidates: string[] = [];
  pushCandidate(candidates, explicitApiBase);
  pushCandidate(candidates, derivedApiBase);

  if (typeof window !== 'undefined') {
    const relativeApiBase = normalizeApiBase(new URL('api', window.location.href).pathname);
    pushCandidate(candidates, relativeApiBase);
  }

  pushCandidate(candidates, '/chat/api');
  pushCandidate(candidates, '/api');
  return candidates;
}

let resolvedApiBase = explicitApiBase ?? derivedApiBase;
let apiBaseResolutionPromise: Promise<string> | null = null;

async function probeApiBase(candidate: string): Promise<boolean> {
  try {
    const response = await fetch(`${candidate}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      return false;
    }

    const contentType = response.headers.get('content-type') ?? '';
    if (!contentType.toLowerCase().includes('application/json')) {
      return false;
    }

    const payload = (await response.json()) as Partial<HealthResponse>;
    return typeof payload.llm_configured === 'boolean';
  } catch {
    return false;
  }
}

async function resolveApiBase(): Promise<string> {
  if (apiBaseResolutionPromise) {
    return apiBaseResolutionPromise;
  }

  const candidates = buildApiBaseCandidates();
  apiBaseResolutionPromise = (async () => {
    for (const candidate of candidates) {
      if (await probeApiBase(candidate)) {
        resolvedApiBase = candidate;
        return candidate;
      }
    }

    return resolvedApiBase;
  })();

  return apiBaseResolutionPromise;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const apiBase = await resolveApiBase();
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = '?붿껌??泥섎━?섏? 紐삵뻽?듬땲??';
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

  try {
    return (await response.json()) as T;
  } catch {
    throw new Error('API 서버 응답 형식을 확인할 수 없습니다. 백엔드 연결 상태를 점검해 주세요.');
  }
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

    const apiBase = await resolveApiBase();
    const response = await fetch(`${apiBase}/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      let message = '臾몄꽌瑜??낅줈?쒗븯吏 紐삵뻽?듬땲??';
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

    try {
      return (await response.json()) as DocumentRecord;
    } catch {
      throw new Error('API 서버 응답 형식을 확인할 수 없습니다. 백엔드 연결 상태를 점검해 주세요.');
    }
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

