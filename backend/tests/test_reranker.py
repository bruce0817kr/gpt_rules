from app.models.schemas import DocumentCategory
from app.services import reranker as reranker_module
from app.services.reranker import BGERerankerService
from app.services.vector_store import SearchHit


class FakeCrossEncoder:
    def __init__(self, model_name: str, **kwargs) -> None:
        self.model_name = model_name
        self.kwargs = kwargs
        self.received_pairs = None
        self.scores = kwargs.pop('scores', [0.1, 3.5, -1.0])

    def predict(self, pairs, convert_to_numpy: bool, show_progress_bar: bool):
        assert convert_to_numpy is True
        assert show_progress_bar is False
        self.received_pairs = pairs
        return self.scores[: len(pairs)]


def test_reranker_initializes_cross_encoder_for_cpu(monkeypatch) -> None:
    captured = {}

    def factory(model_name: str, **kwargs):
        captured['model_name'] = model_name
        captured['kwargs'] = kwargs
        return FakeCrossEncoder(model_name, **kwargs)

    monkeypatch.setattr(reranker_module, 'CrossEncoder', factory)

    BGERerankerService('BAAI/bge-reranker-v2-m3')

    assert captured == {
        'model_name': 'BAAI/bge-reranker-v2-m3',
        'kwargs': {
            'device': 'cpu',
            'automodel_args': {'low_cpu_mem_usage': False},
            'local_files_only': True,
        },
    }


def test_reranker_sorts_hits_by_cross_encoder_score(monkeypatch) -> None:
    fake_model = FakeCrossEncoder('BAAI/bge-reranker-v2-m3')
    monkeypatch.setattr(reranker_module, 'CrossEncoder', lambda model_name, **kwargs: fake_model)

    reranker = BGERerankerService('BAAI/bge-reranker-v2-m3')
    hits = [
        SearchHit('doc-1', 'Doc 1', 'a.txt', DocumentCategory.RULE, 'Section 1', None, 'First', 0.2, 0),
        SearchHit('doc-2', 'Doc 2', 'b.txt', DocumentCategory.RULE, 'Section 2', None, 'Second', 0.3, 1),
        SearchHit('doc-3', 'Doc 3', 'c.txt', DocumentCategory.RULE, 'Section 3', None, 'Third', 0.4, 2),
    ]

    reranked = reranker.rerank('Question', hits, top_k=2)

    assert fake_model.received_pairs == [
        ('Question', 'Title: Doc 1\nFilename: a.txt\nCategory: rule\nLocation: Section 1\nChunk: 0\nBody: First'),
        ('Question', 'Title: Doc 2\nFilename: b.txt\nCategory: rule\nLocation: Section 2\nChunk: 1\nBody: Second'),
        ('Question', 'Title: Doc 3\nFilename: c.txt\nCategory: rule\nLocation: Section 3\nChunk: 2\nBody: Third'),
    ]
    assert [hit.document_id for hit in reranked] == ['doc-2', 'doc-1']
    assert 0.0 < reranked[0].score <= 1.0


def test_reranker_includes_metadata_in_context(monkeypatch) -> None:
    fake_model = FakeCrossEncoder('BAAI/bge-reranker-v2-m3', scores=[0.1])
    monkeypatch.setattr(reranker_module, 'CrossEncoder', lambda model_name, **kwargs: fake_model)

    reranker = BGERerankerService('BAAI/bge-reranker-v2-m3')
    hits = [
        SearchHit(
            'doc-1',
            'Policy Guide',
            'travel.md',
            DocumentCategory.RULE,
            'Chapter 3 > Section 10',
            3,
            'Expense rules apply here.',
            0.2,
            0,
            child_id='child-1',
            parent_id='parent-1',
            path_key='Chapter 3>Section 10>Clause 1',
            source_type=None,
            is_addendum=True,
            is_appendix=False,
        ),
    ]

    reranker.rerank('Question', hits, top_k=1)

    assert fake_model.received_pairs == [
        (
            'Question',
            (
                'Title: Policy Guide\n'
                'Filename: travel.md\n'
                'Category: rule\n'
                'Location: Chapter 3 > Section 10\n'
                'Page: 3\n'
                'Chunk: 0\n'
                'Parent: parent-1\n'
                'Child: child-1\n'
                'Path: Chapter 3>Section 10>Clause 1\n'
                'Flags: addendum\n'
                'Body: Expense rules apply here.'
            ),
        ),
    ]
