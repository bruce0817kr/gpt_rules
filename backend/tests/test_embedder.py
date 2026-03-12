from app.services import embedder as embedder_module
from app.services.embedder import SentenceTransformerEmbedder


class FakeSentenceTransformer:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.calls: list[list[str]] = []

    def encode(
        self,
        texts: list[str],
        normalize_embeddings: bool,
        convert_to_numpy: bool,
        show_progress_bar: bool,
    ) -> list[list[float]]:
        assert normalize_embeddings is True
        assert convert_to_numpy is True
        assert show_progress_bar is False
        self.calls.append(texts)
        return [[1.0, 2.0, 3.0] for _ in texts]


def test_koe5_prefixes_query_and_passage(monkeypatch) -> None:
    fake_model = FakeSentenceTransformer("nlpai-lab/KoE5")
    monkeypatch.setattr(embedder_module, "SentenceTransformer", lambda model_name: fake_model)

    embedder = SentenceTransformerEmbedder("nlpai-lab/KoE5")
    embedder.embed_passages(["규정 본문"])
    embedder.embed_query("정산 기한이 뭐야?")

    assert fake_model.calls[0] == ["passage: 규정 본문"]
    assert fake_model.calls[1] == ["query: 정산 기한이 뭐야?"]
    assert embedder.vector_size() == 3


def test_non_e5_model_uses_plain_text(monkeypatch) -> None:
    fake_model = FakeSentenceTransformer("other-model")
    monkeypatch.setattr(embedder_module, "SentenceTransformer", lambda model_name: fake_model)

    embedder = SentenceTransformerEmbedder("other-model")
    embedder.embed_passages(["plain passage"])
    embedder.embed_query("plain query")

    assert fake_model.calls[0] == ["plain passage"]
    assert fake_model.calls[1] == ["plain query"]
