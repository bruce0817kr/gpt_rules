from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self._vector_size: int | None = None
        self._uses_e5_prefix = "e5" in model_name.lower()

    def vector_size(self) -> int:
        if self._vector_size is None:
            self._vector_size = len(self.embed_passages(["규정 문서 임베딩 샘플"])[0])
        return self._vector_size

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        prepared_texts = (
            [f"passage: {text}" for text in texts]
            if self._uses_e5_prefix
            else texts
        )
        vectors = self.model.encode(
            prepared_texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return [self._to_vector(vector) for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        prepared_text = f"query: {text}" if self._uses_e5_prefix else text
        vectors = self.model.encode(
            [prepared_text],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return self._to_vector(vectors[0])

    def _to_vector(self, vector: object) -> list[float]:
        if hasattr(vector, "tolist"):
            return [float(value) for value in vector.tolist()]
        return [float(value) for value in vector]
