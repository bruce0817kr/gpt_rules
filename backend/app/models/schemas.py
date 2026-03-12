from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class DocumentCategory(str, Enum):
    FOUNDATION = "foundation"
    RULE = "rule"
    LAW = "law"
    GUIDE = "guide"
    NOTICE = "notice"
    OTHER = "other"


class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class LibraryShortcutScope(str, Enum):
    HR = "hr"
    FINANCE = "finance"
    GENERAL_AFFAIRS = "general_affairs"
    GENERAL_ADMIN = "general_admin"
    LEGAL = "legal"


class CategorySource(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"


class AnswerMode(str, Enum):
    STANDARD = "standard"
    HR_ADMIN = "hr_admin"
    CONTRACT_REVIEW = "contract_review"
    PROJECT_MANAGEMENT = "project_management"
    PROCUREMENT_BID = "procurement_bid"
    AUDIT_RESPONSE = "audit_response"


class FeedbackLabel(str, Enum):
    GOOD = "good"
    BAD = "bad"


class FeedbackReasonCode(str, Enum):
    ANSWER_INCORRECT = "answer_incorrect"
    GROUNDING_WEAK = "grounding_weak"
    CITATION_MISMATCH = "citation_mismatch"
    MISSING_DETAIL = "missing_detail"
    FORMAT_POOR = "format_poor"
    OUTDATED_OR_CONFLICT = "outdated_or_conflict"


class DocumentDomain(str, Enum):
    HR = "hr"
    FINANCE = "finance"
    GENERAL_AFFAIRS = "general_affairs"
    GENERAL_ADMIN = "general_admin"
    LEGAL = "legal"
    PROCUREMENT = "procurement"
    RESEARCH = "research"
    OTHER = "other"


class DocumentRecord(BaseModel):
    id: str
    title: str
    filename: str
    stored_filename: str
    file_path: str
    content_type: str | None = None
    category: DocumentCategory = DocumentCategory.OTHER
    category_source: CategorySource = CategorySource.AUTO
    domain: DocumentDomain = DocumentDomain.OTHER
    source_id: str | None = None
    source_version: str | None = None
    source_url: str | None = None
    content_hash: str | None = None
    tags: list[str] = Field(default_factory=list)
    status: DocumentStatus = DocumentStatus.PROCESSING
    uploaded_at: datetime
    updated_at: datetime
    page_count: int = 0
    chunk_count: int = 0
    error_message: str | None = None


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    categories: list[DocumentCategory] = Field(default_factory=list)
    top_k: int | None = Field(default=None, ge=1, le=12)
    answer_mode: AnswerMode = AnswerMode.STANDARD


class Citation(BaseModel):
    index: int
    document_id: str
    title: str
    filename: str
    category: DocumentCategory
    location: str
    page_number: int | None = None
    snippet: str
    score: float


class ChatResponse(BaseModel):
    response_id: str
    generated_at: datetime
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: str
    disclaimer: str
    retrieved_chunks: int


class ChatFeedbackRequest(BaseModel):
    response_id: str = Field(min_length=8, max_length=128)
    rating: FeedbackLabel
    reason_codes: list[FeedbackReasonCode] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def validate_reason_codes(self) -> "ChatFeedbackRequest":
        if self.rating == FeedbackLabel.BAD and not self.reason_codes:
            raise ValueError("Bad feedback requires at least one reason code.")
        self.reason_codes = list(dict.fromkeys(self.reason_codes))
        return self


class ChatFeedbackResponse(BaseModel):
    feedback_id: str
    response_id: str
    rating: FeedbackLabel
    reason_codes: list[FeedbackReasonCode] = Field(default_factory=list)
    recorded_at: datetime
    superseded_feedback_id: str | None = None


class HealthResponse(BaseModel):
    status: str
    documents: int
    llm_configured: bool


class LibrarySearchRequest(BaseModel):
    scope: LibraryShortcutScope
    query: str = ""
    limit: int = Field(default=12, ge=1, le=30)


class LibrarySearchResult(BaseModel):
    document_id: str
    title: str
    filename: str
    category: DocumentCategory
    location: str
    snippet: str
    score: float


class LibrarySearchResponse(BaseModel):
    scope: LibraryShortcutScope
    query: str
    total_documents: int
    results: list[LibrarySearchResult] = Field(default_factory=list)


class CategoryDocumentSearchRequest(BaseModel):
    category: DocumentCategory
    query: str = ""
    limit: int = Field(default=20, ge=1, le=50)


class CategoryDocumentSearchResponse(BaseModel):
    category: DocumentCategory
    query: str
    total_documents: int
    results: list[LibrarySearchResult] = Field(default_factory=list)


class DocumentCategoryUpdateRequest(BaseModel):
    category: DocumentCategory


class DocumentContentSection(BaseModel):
    location: str
    page_number: int | None = None
    text: str


class DocumentContentResponse(BaseModel):
    document_id: str
    title: str
    filename: str
    category: DocumentCategory
    focus_location: str | None = None
    sections: list[DocumentContentSection] = Field(default_factory=list)


class LawImportRequest(BaseModel):
    law_name: str = Field(min_length=2, max_length=200)
