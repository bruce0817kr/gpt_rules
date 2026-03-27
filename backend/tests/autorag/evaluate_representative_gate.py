from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from .compare_representative_runs import build_case_comparisons, load_cases, load_run_outputs
except ImportError:
    from compare_representative_runs import build_case_comparisons, load_cases, load_run_outputs

PREVIEW_PREFIX = 'Retrieved evidence is weak'


@dataclass(frozen=True)
class GateMetrics:
    split: str
    case_count: int
    mean_keyword_coverage_baseline: float
    mean_keyword_coverage_candidate: float
    mean_keyword_coverage_delta: float
    preview_rate_baseline: float
    preview_rate_candidate: float
    preview_rate_delta: float
    worst_case_coverage_delta: float
    regressions_over_threshold: int
    segment_reports: dict[str, dict[str, dict[str, float]]] = field(default_factory=dict)


@dataclass(frozen=True)
class GateDecision:
    passed: bool
    split: str
    reasons: list[str]
    metrics: GateMetrics


def filter_cases_by_split(cases: list[dict[str, Any]], split: str) -> tuple[list[dict[str, Any]], list[int]]:
    selected_cases: list[dict[str, Any]] = []
    selected_indices: list[int] = []
    for index, case in enumerate(cases):
        if split == 'all' or str(case.get('split', '')).strip() == split:
            selected_cases.append(case)
            selected_indices.append(index)
    return selected_cases, selected_indices


def _select_rows(frame: pd.DataFrame, indices: list[int]) -> pd.DataFrame:
    if not indices:
        return frame.iloc[0:0].copy()
    return frame.iloc[indices].reset_index(drop=True)


def _is_preview(text: str) -> bool:
    return str(text).startswith(PREVIEW_PREFIX)




def _segment_summary(rows: list[tuple[dict[str, Any], Any]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    preview_flags: dict[str, list[float]] = defaultdict(list)
    for case, comparison in rows:
        grouped[str(case['segment_value'])].append(float(comparison.coverage_delta))
        preview_flags[str(case['segment_value'])].append(1.0 if str(comparison.candidate_preview).startswith(PREVIEW_PREFIX) else 0.0)
    return {
        key: {
            'count': float(len(values)),
            'mean_coverage_delta': round(sum(values) / len(values), 4),
            'preview_rate_candidate': round(sum(preview_flags[key]) / len(preview_flags[key]), 4),
        }
        for key, values in grouped.items()
    }


def build_segment_reports(cases: list[dict[str, Any]], comparisons: list[Any]) -> dict[str, dict[str, dict[str, float]]]:
    reports: dict[str, dict[str, dict[str, float]]] = {}
    for segment_key in ['doc_type', 'query_type', 'document_named', 'difficulty']:
        rows = []
        for case, comparison in zip(cases, comparisons, strict=True):
            segment_value = case.get(segment_key, 'unknown')
            rows.append(({**case, 'segment_value': segment_value}, comparison))
        reports[segment_key] = _segment_summary(rows)
    return reports

def compute_gate_metrics(
    cases: list[dict[str, Any]],
    baseline_outputs: dict[str, pd.DataFrame],
    candidate_outputs: dict[str, pd.DataFrame],
    *,
    split: str,
) -> GateMetrics:
    selected_cases, selected_indices = filter_cases_by_split(cases, split)
    if not selected_cases:
        raise ValueError(f'No representative cases found for split={split!r}')

    baseline_subset = {
        name: _select_rows(frame, selected_indices)
        for name, frame in baseline_outputs.items()
    }
    candidate_subset = {
        name: _select_rows(frame, selected_indices)
        for name, frame in candidate_outputs.items()
    }

    comparisons = build_case_comparisons(selected_cases, baseline_subset, candidate_subset)
    baseline_coverages = [comparison.baseline_coverage for comparison in comparisons]
    candidate_coverages = [comparison.candidate_coverage for comparison in comparisons]
    coverage_deltas = [comparison.coverage_delta for comparison in comparisons]

    baseline_generation = baseline_subset['generation']
    candidate_generation = candidate_subset['generation']
    baseline_preview_rate = baseline_generation['generated_texts'].map(_is_preview).mean()
    candidate_preview_rate = candidate_generation['generated_texts'].map(_is_preview).mean()

    regressions_over_threshold = sum(1 for delta in coverage_deltas if delta <= -0.20)

    return GateMetrics(
        split=split,
        case_count=len(selected_cases),
        mean_keyword_coverage_baseline=round(sum(baseline_coverages) / len(baseline_coverages), 4),
        mean_keyword_coverage_candidate=round(sum(candidate_coverages) / len(candidate_coverages), 4),
        mean_keyword_coverage_delta=round(sum(coverage_deltas) / len(coverage_deltas), 4),
        preview_rate_baseline=round(float(baseline_preview_rate), 4),
        preview_rate_candidate=round(float(candidate_preview_rate), 4),
        preview_rate_delta=round(float(candidate_preview_rate - baseline_preview_rate), 4),
        worst_case_coverage_delta=round(min(coverage_deltas), 4),
        regressions_over_threshold=regressions_over_threshold,
        segment_reports=build_segment_reports(selected_cases, comparisons),
    )


def evaluate_gate(metrics: GateMetrics) -> GateDecision:
    reasons: list[str] = []

    if metrics.mean_keyword_coverage_delta < 0:
        reasons.append('mean keyword coverage regressed')
    if metrics.preview_rate_delta > 0.15:
        reasons.append('preview-only rate increased too much')
    if metrics.worst_case_coverage_delta <= -0.35:
        reasons.append('worst-case coverage regression is too large')
    if metrics.regressions_over_threshold >= max(2, metrics.case_count // 2 + 1):
        reasons.append('too many cases regressed materially')

    return GateDecision(
        passed=not reasons,
        split=metrics.split,
        reasons=reasons,
        metrics=metrics,
    )


def format_decision(decision: GateDecision, baseline_name: str, candidate_name: str) -> str:
    status = 'PASS' if decision.passed else 'FAIL'
    metrics = decision.metrics
    lines = [
        f'# Representative {metrics.split.title()} Gate',
        '',
        f'- Baseline: `{baseline_name}`',
        f'- Candidate: `{candidate_name}`',
        f'- Result: **{status}**',
        f'- Cases: {metrics.case_count}',
        '',
        '## Metrics',
        '',
        f'- Mean keyword coverage: {metrics.mean_keyword_coverage_baseline:.4f} -> {metrics.mean_keyword_coverage_candidate:.4f} ({metrics.mean_keyword_coverage_delta:+.4f})',
        f'- Preview rate: {metrics.preview_rate_baseline:.4f} -> {metrics.preview_rate_candidate:.4f} ({metrics.preview_rate_delta:+.4f})',
        f'- Worst-case coverage delta: {metrics.worst_case_coverage_delta:+.4f}',
        f'- Regressions over threshold: {metrics.regressions_over_threshold}',
        '',
        '## Reasons',
        '',
    ]
    if decision.reasons:
        lines.extend(f'- {reason}' for reason in decision.reasons)
    else:
        lines.append('- Gate passed: no blocking regression criteria were triggered.')
    lines.extend(['', '## Segment Reports', ''])
    for segment_key, report in metrics.segment_reports.items():
        lines.append(f'### {segment_key}')
        for segment_value, values in sorted(report.items()):
            lines.append(
                f"- {segment_value}: count={int(values['count'])}, mean_coverage_delta={values['mean_coverage_delta']:+.4f}, preview_rate_candidate={values['preview_rate_candidate']:.4f}"
            )
        lines.append('')
    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description='Evaluate PASS/FAIL for a representative split.')
    parser.add_argument('--cases-path', type=Path, default=Path(__file__).with_name('representative_cases.json'))
    parser.add_argument('--baseline-output-dir', type=Path, required=True)
    parser.add_argument('--candidate-output-dir', type=Path, required=True)
    parser.add_argument('--split', choices=['dev', 'validation', 'holdout'], default='validation')
    parser.add_argument('--output-dir', type=Path, default=Path('/app/data/autorag/representative'))
    parser.add_argument('--run-id', type=str, default='gate')
    args = parser.parse_args()

    cases = load_cases(args.cases_path)
    baseline_outputs = load_run_outputs(args.baseline_output_dir)
    candidate_outputs = load_run_outputs(args.candidate_output_dir)
    metrics = compute_gate_metrics(cases, baseline_outputs, candidate_outputs, split=args.split)
    decision = evaluate_gate(metrics)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / f'representative_gate_{args.split}_{args.run_id}.md'
    json_path = args.output_dir / f'representative_gate_{args.split}_{args.run_id}.json'

    report_path.write_text(
        format_decision(decision, args.baseline_output_dir.name, args.candidate_output_dir.name),
        encoding='utf-8',
    )
    json_path.write_text(json.dumps({'decision': asdict(decision), 'metrics': asdict(metrics)}, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'{args.split} gate: {"PASS" if decision.passed else "FAIL"}')
    print(f'Saved report: {report_path}')
    print(f'Saved json: {json_path}')


if __name__ == '__main__':
    main()
