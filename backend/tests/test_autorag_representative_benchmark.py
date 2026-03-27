from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

pd = pytest.importorskip('pandas')


def load_compare_module():
    module_path = Path(__file__).parent / 'autorag' / 'compare_representative_runs.py'
    spec = importlib.util.spec_from_file_location('autorag_compare_representative_runs', module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_run_outputs(
    run_dir: Path,
    *,
    retrieval_f1_on: float,
    retrieval_f1_off: float,
    bleu: float,
    rouge: float,
    answers: list[str],
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {'retrieval_f1': retrieval_f1_on, 'retrieval_recall': retrieval_f1_on, 'retrieval_precision': retrieval_f1_on},
            {'retrieval_f1': retrieval_f1_on - 0.1, 'retrieval_recall': retrieval_f1_on - 0.1, 'retrieval_precision': retrieval_f1_on - 0.1},
        ]
    ).to_csv(run_dir / 'retrieval_eval_reranker_on.csv', index=False)
    pd.DataFrame(
        [
            {'retrieval_f1': retrieval_f1_off, 'retrieval_recall': retrieval_f1_off, 'retrieval_precision': retrieval_f1_off},
            {'retrieval_f1': retrieval_f1_off - 0.1, 'retrieval_recall': retrieval_f1_off - 0.1, 'retrieval_precision': retrieval_f1_off - 0.1},
        ]
    ).to_csv(run_dir / 'retrieval_eval_reranker_off.csv', index=False)
    pd.DataFrame(
        [
            {'generated_texts': answers[0], 'bleu': bleu, 'rouge': rouge},
            {'generated_texts': answers[1], 'bleu': bleu - 0.1, 'rouge': rouge - 0.1},
        ]
    ).to_csv(run_dir / 'generation_eval.csv', index=False)


def test_representative_manifest_uses_expected_domains() -> None:
    module = load_compare_module()
    cases = module.load_cases(Path(__file__).parent / 'autorag' / 'representative_cases.json')

    assert [case['id'] for case in cases] == [
        'travel_expense_approval',
        'disciplinary_procedure_notice',
        'vehicle_management_log',
        'contract_review_change_order',
        'facility_law_lookup',
        'procurement_quote_threshold',
        'leave_process_policy',
        'audit_evidence_retention',
    ]
    assert cases[0]['expected_keywords'] == ['사전 승인', '증빙', '숙박비', '교통비']
    assert cases[3]['answer_mode'] == 'contract_review'


def test_comparison_harness_reports_keyword_coverage_and_deltas(tmp_path) -> None:
    module = load_compare_module()
    cases_path = tmp_path / 'representative_cases.json'
    cases_path.write_text(
        json.dumps(
            [
                {
                    'id': 'travel',
                    'focus_area': 'travel expense rules',
                    'question': '출장비 정산은 어떻게 하나요?',
                    'answer_mode': 'project_management',
                    'categories': ['rule'],
                    'expected_keywords': ['사전 승인', '증빙'],
                },
                {
                    'id': 'discipline',
                    'focus_area': 'disciplinary procedures',
                    'question': '징계 절차는 어떻게 하나요?',
                    'answer_mode': 'hr_admin',
                    'categories': ['rule'],
                    'expected_keywords': ['사전 통지', '소명'],
                },
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding='utf-8',
    )

    baseline_dir = tmp_path / 'baseline'
    candidate_dir = tmp_path / 'candidate'
    write_run_outputs(
        baseline_dir,
        retrieval_f1_on=0.4,
        retrieval_f1_off=0.2,
        bleu=0.1,
        rouge=0.2,
        answers=['사전 승인 없이 정산', '통지만 하면 된다'],
    )
    write_run_outputs(
        candidate_dir,
        retrieval_f1_on=0.8,
        retrieval_f1_off=0.5,
        bleu=0.7,
        rouge=0.8,
        answers=['사전 승인과 증빙이 필요하다', '사전 통지와 소명이 필요하다'],
    )

    cases = module.load_cases(cases_path)
    baseline_outputs = module.load_run_outputs(baseline_dir)
    candidate_outputs = module.load_run_outputs(candidate_dir)
    comparisons = module.build_case_comparisons(cases, baseline_outputs, candidate_outputs)
    summary = module.build_summary(cases, baseline_outputs, candidate_outputs, comparisons)
    report = module.format_markdown(summary, comparisons, 'baseline', 'candidate')

    assert comparisons[0].baseline_coverage == 0.5
    assert comparisons[0].candidate_coverage == 1.0
    assert comparisons[0].retrieval_f1_on_delta == 0.4
    assert summary['delta']['keyword_coverage'] == 0.75
    assert 'Keyword coverage' in report
    assert 'travel expense rules' in report



