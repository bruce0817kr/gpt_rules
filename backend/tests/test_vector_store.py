import sys
import types
from datetime import datetime, timezone
from types import SimpleNamespace

if "docx" not in sys.modules:
    docx_module = types.ModuleType("docx")
    docx_module.Document = object
    sys.modules["docx"] = docx_module

from app.models.schemas import ChunkSourceType, DocumentCategory, DocumentRecord
from app.services.vector_store import QdrantVectorStore


class FakeQdrantClient:
    def __init__(self, *args, **kwargs) -> None:
        self.upsert_calls: list[dict] = []
        self.query_points_calls: list[dict] = []

    def upsert(self, *, collection_name, points, wait) -> None:
        self.upsert_calls.append(
            {
                "collection_name": collection_name,
                "points": points,
                "wait": wait,
            }
        )

    def query_points(self, *, collection_name, query, query_filter, limit, with_payload):
        self.query_points_calls.append(
            {
                "collection_name": collection_name,
                "query": query,
                "query_filter": query_filter,
                "limit": limit,
                "with_payload": with_payload,
            }
        )
        return SimpleNamespace(
            points=[
                SimpleNamespace(
                    score=0.91,
                    payload={
                        "document_id": "doc-1",
                        "title": "여비 규정",
                        "filename": "travel.md",
                        "category": DocumentCategory.RULE.value,
                        "location": "제10조 제1항",
                        "page_number": 3,
                        "text": "제10조 출장비 지급 기준은 다음과 같다.",
                        "chunk_index": 0,
                        "child_id": "child-1",
                        "parent_id": "parent-1",
                        "path_key": "제3장>제10조>제1항",
                        "source_type": "article",
                        "is_addendum": False,
                        "is_appendix": False,
                    },
                )
            ]
        )


class FakeEmbedder:
    def vector_size(self) -> int:
        return 3

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return [[float(index), 0.0, 0.0] for index, _ in enumerate(texts)]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def test_upsert_document_preserves_child_parent_metadata(monkeypatch) -> None:
    monkeypatch.setattr("app.services.vector_store.QdrantClient", FakeQdrantClient)
    monkeypatch.setattr(QdrantVectorStore, "ensure_collection", lambda self: None)

    store = QdrantVectorStore(
        settings=SimpleNamespace(collection_name="documents", qdrant_host="localhost", qdrant_port=6333),
        embedder=FakeEmbedder(),
    )
    record = DocumentRecord(
        id="doc-1",
        title="여비 규정",
        filename="travel.md",
        stored_filename="doc-1.md",
        file_path="/tmp/doc-1.md",
        category=DocumentCategory.RULE,
        uploaded_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    chunk = SimpleNamespace(
        text="제10조 출장비 지급 기준은 다음과 같다.",
        location="제10조 제1항",
        page_number=3,
        chunk_index=0,
        child_id="child-1",
        parent_id="parent-1",
        path_key="제3장>제10조>제1항",
        source_type="article",
        is_addendum=False,
        is_appendix=False,
    )

    count = store.upsert_document(record, [chunk])

    assert count == 1
    payload = store.client.upsert_calls[0]["points"][0].payload
    assert payload["document_id"] == "doc-1"
    assert payload["child_id"] == "child-1"
    assert payload["parent_id"] == "parent-1"
    assert payload["path_key"] == "제3장>제10조>제1항"
    assert payload["source_type"] == "article"
    assert payload["is_addendum"] is False
    assert payload["is_appendix"] is False


def test_search_returns_child_parent_metadata(monkeypatch) -> None:
    monkeypatch.setattr("app.services.vector_store.QdrantClient", FakeQdrantClient)
    monkeypatch.setattr(QdrantVectorStore, "ensure_collection", lambda self: None)

    store = QdrantVectorStore(
        settings=SimpleNamespace(collection_name="documents", qdrant_host="localhost", qdrant_port=6333),
        embedder=FakeEmbedder(),
    )

    hits = store.search(question="출장비 기준이 뭐야?", categories=[DocumentCategory.RULE], top_k=5)

    assert len(hits) == 1
    hit = hits[0]
    assert hit.child_id == "child-1"
    assert hit.parent_id == "parent-1"
    assert hit.path_key == "제3장>제10조>제1항"
    assert hit.source_type == ChunkSourceType.ARTICLE
    assert hit.is_addendum is False
    assert hit.is_appendix is False


def test_search_uses_document_id_filter_when_shortlisted(monkeypatch) -> None:
    monkeypatch.setattr("app.services.vector_store.QdrantClient", FakeQdrantClient)
    monkeypatch.setattr(QdrantVectorStore, "ensure_collection", lambda self: None)

    store = QdrantVectorStore(
        settings=SimpleNamespace(collection_name="documents", qdrant_host="localhost", qdrant_port=6333),
        embedder=FakeEmbedder(),
    )

    store.search(
        question='?????? ?? ??? ???? ????',
        categories=[DocumentCategory.RULE],
        top_k=5,
        document_ids=['doc-1', 'doc-2'],
    )

    query_filter = store.client.query_points_calls[0]['query_filter']
    document_condition = query_filter.must[0]
    assert document_condition.key == 'document_id'
    assert document_condition.match.any == ['doc-1', 'doc-2']


def test_upsert_document_batches_large_point_sets(monkeypatch) -> None:
    monkeypatch.setattr("app.services.vector_store.QdrantClient", FakeQdrantClient)
    monkeypatch.setattr(QdrantVectorStore, "ensure_collection", lambda self: None)
    monkeypatch.setattr(QdrantVectorStore, "UPSERT_BATCH_SIZE", 2)

    store = QdrantVectorStore(
        settings=SimpleNamespace(collection_name="documents", qdrant_host="localhost", qdrant_port=6333),
        embedder=FakeEmbedder(),
    )
    record = DocumentRecord(
        id="doc-1",
        title="Travel Rules",
        filename="travel.md",
        stored_filename="doc-1.md",
        file_path="/tmp/doc-1.md",
        category=DocumentCategory.RULE,
        uploaded_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    chunks = [
        SimpleNamespace(
            text=f"chunk {index}",
            location=f"Section {index}",
            page_number=1,
            chunk_index=index,
            child_id=f"child-{index}",
            parent_id=f"parent-{index}",
            path_key=f"path-{index}",
            source_type="article",
            is_addendum=False,
            is_appendix=False,
        )
        for index in range(5)
    ]

    count = store.upsert_document(record, chunks)

    assert count == 5
    assert len(store.client.upsert_calls) == 3
    assert [len(call["points"]) for call in store.client.upsert_calls] == [2, 2, 1]
