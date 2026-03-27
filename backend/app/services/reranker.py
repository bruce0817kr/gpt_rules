from math import exp

from sentence_transformers import CrossEncoder

from app.services.vector_store import SearchHit


class BGERerankerService:
    def __init__(self, model_name: str) -> None:
        self.model = CrossEncoder(model_name, device='cpu', automodel_args={'low_cpu_mem_usage': False}, local_files_only=True)

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
        lines = [
            f'Title: {hit.title}',
            f'Filename: {hit.filename}',
            f'Category: {hit.category.value}',
            f'Location: {hit.location}',
        ]
        if hit.page_number is not None:
            lines.append(f'Page: {hit.page_number}')
        lines.append(f'Chunk: {hit.chunk_index}')
        if hit.parent_id:
            lines.append(f'Parent: {hit.parent_id}')
        if hit.child_id:
            lines.append(f'Child: {hit.child_id}')
        if hit.path_key:
            lines.append(f'Path: {hit.path_key}')
        if hit.source_type is not None:
            source_type = hit.source_type.value if hasattr(hit.source_type, 'value') else str(hit.source_type)
            lines.append(f'Source type: {source_type}')
        flags: list[str] = []
        if hit.is_addendum:
            flags.append('addendum')
        if hit.is_appendix:
            flags.append('appendix')
        if flags:
            lines.append(f'Flags: {", ".join(flags)}')
        lines.append(f'Body: {hit.snippet}')
        return '\n'.join(lines)

    def _sigmoid(self, value: float) -> float:
        return 1.0 / (1.0 + exp(-value))

