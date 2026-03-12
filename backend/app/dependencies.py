from functools import lru_cache

from app.config import get_settings
from app.services.catalog import DocumentCatalog
from app.services.category_classifier import DocumentCategoryClassifier
from app.services.chat import ChatService
from app.services.chunker import Chunker
from app.services.document_parser import DocumentParser
from app.services.embedder import SentenceTransformerEmbedder
from app.services.feedback_store import ChatFeedbackStore
from app.services.ingestion import DocumentIngestionService
from app.services.library_search import LibrarySearchService
from app.services.law_sync import LawSyncService
from app.services.reranker import BGERerankerService
from app.services.shortcut_scope import ShortcutScopeMatcher
from app.services.vector_store import QdrantVectorStore


@lru_cache
def get_catalog() -> DocumentCatalog:
    settings = get_settings()
    return DocumentCatalog(settings.data_dir / "documents.sqlite3")


@lru_cache
def get_parser() -> DocumentParser:
    return DocumentParser()


@lru_cache
def get_chunker() -> Chunker:
    settings = get_settings()
    return Chunker(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)


@lru_cache
def get_category_classifier() -> DocumentCategoryClassifier:
    return DocumentCategoryClassifier()


@lru_cache
def get_shortcut_scope_matcher() -> ShortcutScopeMatcher:
    return ShortcutScopeMatcher()


@lru_cache
def get_embedder() -> SentenceTransformerEmbedder:
    settings = get_settings()
    return SentenceTransformerEmbedder(model_name=settings.embedding_model)


@lru_cache
def get_reranker() -> BGERerankerService:
    settings = get_settings()
    return BGERerankerService(model_name=settings.reranker_model)


@lru_cache
def get_feedback_store() -> ChatFeedbackStore:
    settings = get_settings()
    return ChatFeedbackStore(settings.data_dir / "feedback")


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    settings = get_settings()
    embedder = get_embedder()
    return QdrantVectorStore(settings=settings, embedder=embedder)


@lru_cache
def get_ingestion_service() -> DocumentIngestionService:
    settings = get_settings()
    return DocumentIngestionService(
        settings=settings,
        catalog=get_catalog(),
        parser=get_parser(),
        chunker=get_chunker(),
        category_classifier=get_category_classifier(),
        vector_store=get_vector_store(),
    )


@lru_cache
def get_library_search_service() -> LibrarySearchService:
    return LibrarySearchService(
        catalog=get_catalog(),
        parser=get_parser(),
        scope_matcher=get_shortcut_scope_matcher(),
    )


@lru_cache
def get_law_sync_service() -> LawSyncService:
    return LawSyncService(
        settings=get_settings(),
        catalog=get_catalog(),
        ingestion=get_ingestion_service(),
    )


@lru_cache
def get_chat_service() -> ChatService:
    settings = get_settings()
    return ChatService(
        settings=settings,
        vector_store=get_vector_store(),
        reranker=get_reranker(),
        catalog=get_catalog(),
        parser=get_parser(),
        feedback_store=get_feedback_store(),
    )
