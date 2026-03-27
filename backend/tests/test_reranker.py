from app.models.schemas import DocumentCategory
from app.services import reranker as reranker_module
from app.services.reranker import BGERerankerService
from app.services.vector_store import SearchHit


class FakeCrossEncoder:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.received_pairs = None

    def predict(self, pairs, convert_to_numpy: bool, show_progress_bar: bool):
        assert convert_to_numpy is True
        assert show_progress_bar is False
        self.received_pairs = pairs
        return [0.1, 3.5, -1.0]


def test_reranker_sorts_hits_by_cross_encoder_score(monkeypatch) -> None:
    fake_model = FakeCrossEncoder('BAAI/bge-reranker-v2-m3')
    monkeypatch.setattr(reranker_module, 'CrossEncoder', lambda model_name: fake_model)

    reranker = BGERerankerService('BAAI/bge-reranker-v2-m3')
    hits = [
        SearchHit('doc-1', '문서1', 'a.txt', DocumentCategory.RULE, '구간 1', None, '첫번째', 0.2, 0),
        SearchHit('doc-2', '문서2', 'b.txt', DocumentCategory.RULE, '구간 2', None, '두번째', 0.3, 1),
        SearchHit('doc-3', '문서3', 'c.txt', DocumentCategory.RULE, '구간 3', None, '세번째', 0.4, 2),
    ]

    reranked = reranker.rerank('질문', hits, top_k=2)

    assert fake_model.received_pairs == [
        ('질문', 'Title: 문서1\nLocation: 구간 1\nBody: 첫번째'),
        ('질문', 'Title: 문서2\nLocation: 구간 2\nBody: 두번째'),
        ('질문', 'Title: 문서3\nLocation: 구간 3\nBody: 세번째'),
    ]
    assert [hit.document_id for hit in reranked] == ['doc-2', 'doc-1']
    assert 0.0 < reranked[0].score <= 1.0

