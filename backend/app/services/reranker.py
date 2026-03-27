from math import exp

from sentence_transformers import CrossEncoder

from app.services.vector_store import SearchHit


class BGERerankerService:
    def __init__(self, model_name: str) -> None:
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, hits: list[SearchHit], top_k: int) -> list[SearchHit]:
        if not hits:
            return []

        pairs = [(query, self._format_hit_for_rerank(hit)) for hit in hits]
        scores = self.model.predict(
            pairs,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        ranked_hits = [
            hit.__class__(
                document_id=hit.document_id,
                title=hit.title,
                filename=hit.filename,
                category=hit.category,
                location=hit.location,
                page_number=hit.page_number,
                snippet=hit.snippet,
                score=self._sigmoid(float(score)),
                chunk_index=hit.chunk_index,
            )
            for hit, score in zip(hits, scores, strict=True)
        ]
        ranked_hits.sort(key=lambda item: item.score, reverse=True)
        return ranked_hits[:top_k]

    def _format_hit_for_rerank(self, hit: SearchHit) -> str:
        return f"Title: {hit.title}\nLocation: {hit.location}\nBody: {hit.snippet}"

    def _sigmoid(self, value: float) -> float:
        return 1.0 / (1.0 + exp(-value))
