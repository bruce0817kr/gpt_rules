from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import Settings
from app.models.schemas import ChunkSourceType, DocumentCategory, DocumentRecord
from app.services.chunker import Chunk
from app.services.embedder import SentenceTransformerEmbedder


@dataclass(slots=True)
class SearchHit:
    document_id: str
    title: str
    filename: str
    category: DocumentCategory
    location: str
    page_number: int | None
    snippet: str
    score: float
    chunk_index: int
    child_id: str | None = None
    parent_id: str | None = None
    path_key: str | None = None
    source_type: ChunkSourceType | None = None
    is_addendum: bool = False
    is_appendix: bool = False


class QdrantVectorStore:
    def __init__(self, settings: Settings, embedder: SentenceTransformerEmbedder) -> None:
        self.collection_name = settings.collection_name
        self.embedder = embedder
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            check_compatibility=False,
        )

    def ensure_collection(self) -> None:
        target_size = self.embedder.vector_size()
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection_name for collection in collections):
            self._create_collection(target_size)
            return

        current_size = self._collection_vector_size()
        if current_size == target_size:
            return

        self.client.delete_collection(collection_name=self.collection_name)
        self._create_collection(target_size)

    def _create_collection(self, vector_size: int) -> None:
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    def _collection_vector_size(self) -> int | None:
        collection_info = self.client.get_collection(self.collection_name)
        vector_config = collection_info.config.params.vectors
        if isinstance(vector_config, dict):
            first_vector = next(iter(vector_config.values()), None)
            return getattr(first_vector, "size", None)
        return getattr(vector_config, "size", None)

    def upsert_document(self, record: DocumentRecord, chunks: list[Chunk]) -> int:
        self.ensure_collection()
        texts = [chunk.text for chunk in chunks]
        vectors = self.embedder.embed_passages(texts)
        points: list[models.PointStruct] = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            payload = self._build_payload(record, chunk)
            points.append(models.PointStruct(id=str(uuid4()), vector=vector, payload=payload))
        self.client.upsert(collection_name=self.collection_name, points=points, wait=True)
        return len(points)

    def _build_payload(self, record: DocumentRecord, chunk: Chunk) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "document_id": record.id,
            "title": record.title,
            "filename": record.filename,
            "category": record.category.value,
            "tags": record.tags,
            "location": chunk.location,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
            "is_addendum": bool(getattr(chunk, "is_addendum", False)),
            "is_appendix": bool(getattr(chunk, "is_appendix", False)),
        }
        child_id = getattr(chunk, "child_id", None)
        if child_id is not None:
            payload["child_id"] = child_id
        parent_id = getattr(chunk, "parent_id", None)
        if parent_id is not None:
            payload["parent_id"] = parent_id
        path_key = getattr(chunk, "path_key", None)
        if path_key is not None:
            payload["path_key"] = path_key
        source_type = getattr(chunk, "source_type", None)
        if source_type is not None:
            payload["source_type"] = self._normalize_source_type(source_type)
        return payload

    @staticmethod
    def _normalize_source_type(source_type: Any) -> str:
        if isinstance(source_type, ChunkSourceType):
            return source_type.value
        return str(source_type)

    def delete_document(self, document_id: str) -> None:
        self.ensure_collection()
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            ),
            wait=True,
        )

    def search(
        self,
        question: str,
        categories: list[DocumentCategory],
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> list[SearchHit]:
        self.ensure_collection()
        query_filter = self._build_filter(categories, document_ids)
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=self.embedder.embed_query(question),
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )
        hits: list[SearchHit] = []
        for result in response.points:
            payload = result.payload or {}
            hits.append(
                SearchHit(
                    document_id=str(payload.get("document_id", "")),
                    title=str(payload.get("title", "제목 없음")),
                    filename=str(payload.get("filename", "")),
                    category=DocumentCategory(str(payload.get("category", DocumentCategory.OTHER.value))),
                    location=str(payload.get("location", "본문")),
                    page_number=payload.get("page_number"),
                    snippet=str(payload.get("text", "")),
                    score=float(result.score),
                    chunk_index=int(payload.get("chunk_index", 0)),
                    child_id=payload.get("child_id"),
                    parent_id=payload.get("parent_id"),
                    path_key=payload.get("path_key"),
                    source_type=self._parse_source_type(payload.get("source_type")),
                    is_addendum=bool(payload.get("is_addendum", False)),
                    is_appendix=bool(payload.get("is_appendix", False)),
                )
            )
        return hits

    @staticmethod
    def _parse_source_type(source_type: Any) -> ChunkSourceType | None:
        if source_type is None:
            return None
        try:
            return ChunkSourceType(str(source_type))
        except ValueError:
            return None

    def _build_filter(
        self,
        categories: list[DocumentCategory],
        document_ids: list[str] | None,
    ) -> models.Filter | None:
        must_conditions: list[models.Condition] = []
        should_conditions: list[models.Condition] = []

        if document_ids:
            should_conditions.extend(
                models.FieldCondition(key='document_id', match=models.MatchValue(value=document_id))
                for document_id in document_ids
            )

        if categories:
            if len(categories) == 1:
                must_conditions.append(
                    models.FieldCondition(
                        key='category',
                        match=models.MatchValue(value=categories[0].value),
                    )
                )
            else:
                should_conditions.extend(
                    models.FieldCondition(key='category', match=models.MatchValue(value=category.value))
                    for category in categories
                )

        if not must_conditions and not should_conditions:
            return None
        return models.Filter(must=must_conditions or None, should=should_conditions or None)
