import pandas as pd

from autorag.evaluate_representative_gate import compute_gate_metrics, evaluate_gate, filter_cases_by_split


def _frame(rows):
    return pd.DataFrame(rows)


def test_filter_cases_by_split_returns_expected_indices() -> None:
    cases = [
        {'id': 'a', 'split': 'dev'},
        {'id': 'b', 'split': 'validation'},
        {'id': 'c', 'split': 'holdout'},
    ]

    selected, indices = filter_cases_by_split(cases, 'validation')

    assert [case['id'] for case in selected] == ['b']
    assert indices == [1]


def test_compute_gate_metrics_uses_only_selected_split() -> None:
    cases = [
        {'id': 'a', 'split': 'dev', 'focus_area': 'dev', 'question': 'alpha?', 'expected_keywords': ['alpha']},
        {'id': 'b', 'split': 'validation', 'focus_area': 'validation', 'question': 'beta?', 'expected_keywords': ['beta']},
        {'id': 'c', 'split': 'validation', 'focus_area': 'validation', 'question': 'gamma?', 'expected_keywords': ['gamma']},
    ]
    baseline_outputs = {
        'generation': _frame([
            {'generated_texts': 'alpha', 'bleu': 0.0, 'rouge': 0.0},
            {'generated_texts': 'beta', 'bleu': 0.0, 'rouge': 0.0},
            {'generated_texts': 'gamma', 'bleu': 0.0, 'rouge': 0.0},
        ]),
        'retrieval_on': _frame([{'retrieval_f1': 0.0}] * 3),
        'retrieval_off': _frame([{'retrieval_f1': 0.0}] * 3),
    }
    candidate_outputs = {
        'generation': _frame([
            {'generated_texts': 'alpha', 'bleu': 0.0, 'rouge': 0.0},
            {'generated_texts': 'Retrieved evidence is weak', 'bleu': 0.0, 'rouge': 0.0},
            {'generated_texts': 'gamma extra', 'bleu': 0.0, 'rouge': 0.0},
        ]),
        'retrieval_on': _frame([{'retrieval_f1': 0.0}] * 3),
        'retrieval_off': _frame([{'retrieval_f1': 0.0}] * 3),
    }

    metrics = compute_gate_metrics(cases, baseline_outputs, candidate_outputs, split='validation')

    assert metrics.case_count == 2
    assert metrics.mean_keyword_coverage_baseline == 1.0
    assert metrics.mean_keyword_coverage_candidate == 0.5
    assert metrics.preview_rate_candidate == 0.5


def test_evaluate_gate_fails_on_validation_regression() -> None:
    from autorag.evaluate_representative_gate import GateMetrics

    decision = evaluate_gate(
        GateMetrics(
            split='validation',
            case_count=3,
            mean_keyword_coverage_baseline=0.8,
            mean_keyword_coverage_candidate=0.5,
            mean_keyword_coverage_delta=-0.3,
            preview_rate_baseline=0.0,
            preview_rate_candidate=0.34,
            preview_rate_delta=0.34,
            worst_case_coverage_delta=-0.4,
            regressions_over_threshold=2,
        )
    )

    assert decision.passed is False
    assert len(decision.reasons) >= 1


def test_load_cases_preserves_distribution_metadata() -> None:
    from pathlib import Path
    from autorag.compare_representative_runs import load_cases

    cases = load_cases(Path(r'c:\Project\gpt_rules\.worktrees\gtp-guidebook-redesign\backend\tests\autorag\representative_cases.json'))
    first = cases[0]

    assert first['doc_type']
    assert first['query_type']
    assert isinstance(first['document_named'], bool)
    assert first['difficulty']
    assert first['domain']
    assert first['expected_target_document']
    assert first['expected_source_type']


def test_compute_gate_metrics_builds_segment_reports() -> None:
    cases = [
        {'id': 'a', 'split': 'validation', 'focus_area': 'x', 'question': 'a?', 'expected_keywords': ['alpha'], 'doc_type': 'rule', 'query_type': 'procedure', 'document_named': False, 'difficulty': 'easy'},
        {'id': 'b', 'split': 'validation', 'focus_area': 'x', 'question': 'b?', 'expected_keywords': ['beta'], 'doc_type': 'law', 'query_type': 'criteria', 'document_named': True, 'difficulty': 'hard'},
    ]
    baseline_outputs = {
        'generation': _frame([
            {'generated_texts': 'alpha', 'bleu': 0.0, 'rouge': 0.0},
            {'generated_texts': 'beta', 'bleu': 0.0, 'rouge': 0.0},
        ]),
        'retrieval_on': _frame([{'retrieval_f1': 0.0}] * 2),
        'retrieval_off': _frame([{'retrieval_f1': 0.0}] * 2),
    }
    candidate_outputs = {
        'generation': _frame([
            {'generated_texts': 'alpha', 'bleu': 0.0, 'rouge': 0.0},
            {'generated_texts': 'Retrieved evidence is weak', 'bleu': 0.0, 'rouge': 0.0},
        ]),
        'retrieval_on': _frame([{'retrieval_f1': 0.0}] * 2),
        'retrieval_off': _frame([{'retrieval_f1': 0.0}] * 2),
    }

    metrics = compute_gate_metrics(cases, baseline_outputs, candidate_outputs, split='validation')

    assert 'doc_type' in metrics.segment_reports
    assert 'query_type' in metrics.segment_reports
    assert 'document_named' in metrics.segment_reports
    assert 'difficulty' in metrics.segment_reports
    assert 'rule' in metrics.segment_reports['doc_type']
    assert 'law' in metrics.segment_reports['doc_type']
