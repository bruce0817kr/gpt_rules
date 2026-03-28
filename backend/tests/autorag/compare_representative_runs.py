from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


def load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(payload, list):
        raise ValueError(f'Representative case manifest must be a JSON list: {path}')

    cases: list[dict[str, Any]] = []
    for index, raw_case in enumerate(payload, start=1):
        if not isinstance(raw_case, dict):
            raise ValueError(f'Case #{index} is not an object: {path}')

        case = {
            'id': str(raw_case.get('id', '')).strip(),
            'split': str(raw_case.get('split', '')).strip(),
            'focus_area': str(raw_case.get('focus_area', '')).strip(),
            'doc_type': str(raw_case.get('doc_type', '')).strip(),
            'query_type': str(raw_case.get('query_type', '')).strip(),
            'document_named': bool(raw_case.get('document_named', False)),
            'difficulty': str(raw_case.get('difficulty', '')).strip(),
            'domain': str(raw_case.get('domain', '')).strip(),
            'question': str(raw_case.get('question', '')).strip(),
            'answer_mode': str(raw_case.get('answer_mode', '')).strip(),
            'categories': [str(category).strip() for category in raw_case.get('categories', []) if str(category).strip()],
            'expected_keywords': [
                str(keyword).strip()
                for keyword in raw_case.get('expected_keywords', [])
                if str(keyword).strip()
            ],
            'expected_target_document': str(raw_case.get('expected_target_document', '')).strip(),
            'expected_source_type': str(raw_case.get('expected_source_type', '')).strip(),
            'benchmark_note': str(raw_case.get('benchmark_note', '')).strip(),
        }
        if not case['id'] or not case['question'] or not case['expected_keywords']:
            raise ValueError(f'Case #{index} is missing required fields: {path}')
        cases.append(case)
    return cases


def load_run_outputs(run_dir: Path) -> dict[str, pd.DataFrame]:
    retrieval_on_path = run_dir / 'retrieval_eval_reranker_on.csv'
    retrieval_off_path = run_dir / 'retrieval_eval_reranker_off.csv'
    generation_path = run_dir / 'generation_eval.csv'

    for path in [retrieval_on_path, retrieval_off_path, generation_path]:
        if not path.exists():
            raise FileNotFoundError(f'Missing evaluation artifact: {path}')

    return {
        'retrieval_on': pd.read_csv(retrieval_on_path).reset_index(drop=True),
        'retrieval_off': pd.read_csv(retrieval_off_path).reset_index(drop=True),
        'generation': pd.read_csv(generation_path).reset_index(drop=True),
    }


def normalize_text(value: str) -> str:
    return ' '.join(str(value).split()).strip().lower()


def keyword_coverage(text: str, keywords: list[str]) -> dict[str, Any]:
    normalized_text = normalize_text(text)
    matched_keywords = [keyword for keyword in keywords if normalize_text(keyword) in normalized_text]
    total = len(keywords)
    coverage = (len(matched_keywords) / total) if total else 0.0
    return {
        'matched_keywords': matched_keywords,
        'keyword_total': total,
        'keyword_hits': len(matched_keywords),
        'keyword_coverage': round(coverage, 4),
    }


def summarize_metrics(frame: pd.DataFrame) -> dict[str, float]:
    numeric = frame.mean(numeric_only=True).to_dict()
    return {key: round(float(value), 6) for key, value in numeric.items()}


@dataclass(frozen=True)
class CaseComparison:
    qid: str
    focus_area: str
    question: str
    expected_keywords: list[str]
    baseline_coverage: float
    candidate_coverage: float
    coverage_delta: float
    baseline_retrieval_f1_on: float
    candidate_retrieval_f1_on: float
    retrieval_f1_on_delta: float
    baseline_retrieval_f1_off: float
    candidate_retrieval_f1_off: float
    retrieval_f1_off_delta: float
    baseline_bleu: float
    candidate_bleu: float
    bleu_delta: float
    baseline_rouge: float
    candidate_rouge: float
    rouge_delta: float
    baseline_preview: str
    candidate_preview: str


def build_case_comparisons(
    cases: list[dict[str, Any]],
    baseline_outputs: dict[str, pd.DataFrame],
    candidate_outputs: dict[str, pd.DataFrame],
) -> list[CaseComparison]:
    row_count = len(cases)
    for name, outputs in {'baseline': baseline_outputs, 'candidate': candidate_outputs}.items():
        for frame_name, frame in outputs.items():
            if len(frame) != row_count:
                raise ValueError(
                    f'{name} {frame_name} row count {len(frame)} does not match representative case count {row_count}.'
                )

    comparisons: list[CaseComparison] = []
    for index, case in enumerate(cases):
        baseline_generation = str(baseline_outputs['generation'].iloc[index].get('generated_texts', ''))
        candidate_generation = str(candidate_outputs['generation'].iloc[index].get('generated_texts', ''))
        baseline_coverage = keyword_coverage(baseline_generation, case['expected_keywords'])
        candidate_coverage = keyword_coverage(candidate_generation, case['expected_keywords'])

        baseline_retrieval_on = baseline_outputs['retrieval_on'].iloc[index]
        candidate_retrieval_on = candidate_outputs['retrieval_on'].iloc[index]
        baseline_retrieval_off = baseline_outputs['retrieval_off'].iloc[index]
        candidate_retrieval_off = candidate_outputs['retrieval_off'].iloc[index]
        baseline_generation_row = baseline_outputs['generation'].iloc[index]
        candidate_generation_row = candidate_outputs['generation'].iloc[index]

        comparisons.append(
            CaseComparison(
                qid=case['id'],
                focus_area=case['focus_area'],
                question=case['question'],
                expected_keywords=case['expected_keywords'],
                baseline_coverage=float(baseline_coverage['keyword_coverage']),
                candidate_coverage=float(candidate_coverage['keyword_coverage']),
                coverage_delta=round(
                    float(candidate_coverage['keyword_coverage']) - float(baseline_coverage['keyword_coverage']),
                    4,
                ),
                baseline_retrieval_f1_on=round(float(baseline_retrieval_on.get('retrieval_f1', 0.0)), 4),
                candidate_retrieval_f1_on=round(float(candidate_retrieval_on.get('retrieval_f1', 0.0)), 4),
                retrieval_f1_on_delta=round(
                    float(candidate_retrieval_on.get('retrieval_f1', 0.0))
                    - float(baseline_retrieval_on.get('retrieval_f1', 0.0)),
                    4,
                ),
                baseline_retrieval_f1_off=round(float(baseline_retrieval_off.get('retrieval_f1', 0.0)), 4),
                candidate_retrieval_f1_off=round(float(candidate_retrieval_off.get('retrieval_f1', 0.0)), 4),
                retrieval_f1_off_delta=round(
                    float(candidate_retrieval_off.get('retrieval_f1', 0.0))
                    - float(baseline_retrieval_off.get('retrieval_f1', 0.0)),
                    4,
                ),
                baseline_bleu=round(float(baseline_generation_row.get('bleu', 0.0)), 4),
                candidate_bleu=round(float(candidate_generation_row.get('bleu', 0.0)), 4),
                bleu_delta=round(
                    float(candidate_generation_row.get('bleu', 0.0))
                    - float(baseline_generation_row.get('bleu', 0.0)),
                    4,
                ),
                baseline_rouge=round(float(baseline_generation_row.get('rouge', 0.0)), 4),
                candidate_rouge=round(float(candidate_generation_row.get('rouge', 0.0)), 4),
                rouge_delta=round(
                    float(candidate_generation_row.get('rouge', 0.0))
                    - float(baseline_generation_row.get('rouge', 0.0)),
                    4,
                ),
                baseline_preview=baseline_generation[:240],
                candidate_preview=candidate_generation[:240],
            )
        )

    return comparisons


def build_summary(
    cases: list[dict[str, Any]],
    baseline_outputs: dict[str, pd.DataFrame],
    candidate_outputs: dict[str, pd.DataFrame],
    comparisons: list[CaseComparison],
) -> dict[str, Any]:
    baseline_generation = baseline_outputs['generation'].copy()
    candidate_generation = candidate_outputs['generation'].copy()
    baseline_generation['keyword_coverage'] = [
        keyword_coverage(str(row.get('generated_texts', '')), case['expected_keywords'])['keyword_coverage']
        for case, (_, row) in zip(cases, baseline_generation.iterrows())
    ]
    candidate_generation['keyword_coverage'] = [
        keyword_coverage(str(row.get('generated_texts', '')), case['expected_keywords'])['keyword_coverage']
        for case, (_, row) in zip(cases, candidate_generation.iterrows())
    ]

    summary = {
        'baseline': {
            'retrieval_on_mean': summarize_metrics(baseline_outputs['retrieval_on']),
            'retrieval_off_mean': summarize_metrics(baseline_outputs['retrieval_off']),
            'generation_mean': summarize_metrics(baseline_outputs['generation']),
            'keyword_coverage_mean': round(float(baseline_generation['keyword_coverage'].mean()), 4),
        },
        'candidate': {
            'retrieval_on_mean': summarize_metrics(candidate_outputs['retrieval_on']),
            'retrieval_off_mean': summarize_metrics(candidate_outputs['retrieval_off']),
            'generation_mean': summarize_metrics(candidate_outputs['generation']),
            'keyword_coverage_mean': round(float(candidate_generation['keyword_coverage'].mean()), 4),
        },
    }
    summary['delta'] = {
        'retrieval_f1_on': round(
            summary['candidate']['retrieval_on_mean'].get('retrieval_f1', 0.0)
            - summary['baseline']['retrieval_on_mean'].get('retrieval_f1', 0.0),
            4,
        ),
        'retrieval_f1_off': round(
            summary['candidate']['retrieval_off_mean'].get('retrieval_f1', 0.0)
            - summary['baseline']['retrieval_off_mean'].get('retrieval_f1', 0.0),
            4,
        ),
        'bleu': round(
            summary['candidate']['generation_mean'].get('bleu', 0.0)
            - summary['baseline']['generation_mean'].get('bleu', 0.0),
            4,
        ),
        'rouge': round(
            summary['candidate']['generation_mean'].get('rouge', 0.0)
            - summary['baseline']['generation_mean'].get('rouge', 0.0),
            4,
        ),
        'keyword_coverage': round(
            summary['candidate']['keyword_coverage_mean'] - summary['baseline']['keyword_coverage_mean'],
            4,
        ),
    }

    summary['case_count'] = len(comparisons)
    score = lambda item: item.coverage_delta + item.retrieval_f1_on_delta + item.rouge_delta + item.bleu_delta
    summary['biggest_improvements'] = [asdict(item) for item in sorted(comparisons, key=score, reverse=True)[:3]]
    summary['biggest_regressions'] = [asdict(item) for item in sorted(comparisons, key=score)[:3]]
    return summary


def format_markdown(summary: dict[str, Any], comparisons: list[CaseComparison], baseline_name: str, candidate_name: str) -> str:
    lines = [
        '# Representative AutoRAG Comparison',
        '',
        f'- Baseline: `{baseline_name}`',
        f'- Candidate: `{candidate_name}`',
        f'- Cases: {summary["case_count"]}',
        '',
        '## Summary',
        '',
        '| Metric | Baseline | Candidate | Delta |',
        '| --- | ---: | ---: | ---: |',
        f"| Retrieval F1 (reranker on) | {summary['baseline']['retrieval_on_mean'].get('retrieval_f1', 0.0):.4f} | {summary['candidate']['retrieval_on_mean'].get('retrieval_f1', 0.0):.4f} | {summary['delta']['retrieval_f1_on']:.4f} |",
        f"| Retrieval F1 (reranker off) | {summary['baseline']['retrieval_off_mean'].get('retrieval_f1', 0.0):.4f} | {summary['candidate']['retrieval_off_mean'].get('retrieval_f1', 0.0):.4f} | {summary['delta']['retrieval_f1_off']:.4f} |",
        f"| BLEU | {summary['baseline']['generation_mean'].get('bleu', 0.0):.4f} | {summary['candidate']['generation_mean'].get('bleu', 0.0):.4f} | {summary['delta']['bleu']:.4f} |",
        f"| ROUGE | {summary['baseline']['generation_mean'].get('rouge', 0.0):.4f} | {summary['candidate']['generation_mean'].get('rouge', 0.0):.4f} | {summary['delta']['rouge']:.4f} |",
        f"| Keyword coverage | {summary['baseline']['keyword_coverage_mean']:.4f} | {summary['candidate']['keyword_coverage_mean']:.4f} | {summary['delta']['keyword_coverage']:.4f} |",
        '',
        '## Biggest Improvements',
        '',
    ]
    for comparison in summary['biggest_improvements']:
        lines.extend(
            [
                f"- `{comparison['qid']}` {comparison['focus_area']}",
                f"  coverage_delta={comparison['coverage_delta']:.4f} retrieval_f1_on_delta={comparison['retrieval_f1_on_delta']:.4f} rouge_delta={comparison['rouge_delta']:.4f}",
            ]
        )

    lines.extend(['', '## Biggest Regressions', ''])
    for comparison in summary['biggest_regressions']:
        lines.extend(
            [
                f"- `{comparison['qid']}` {comparison['focus_area']}",
                f"  coverage_delta={comparison['coverage_delta']:.4f} retrieval_f1_on_delta={comparison['retrieval_f1_on_delta']:.4f} rouge_delta={comparison['rouge_delta']:.4f}",
            ]
        )

    lines.extend(['', '## Per-Case Coverage', ''])
    for comparison in comparisons:
        lines.extend(
            [
                f'- `{comparison.qid}` {comparison.focus_area}',
                f'  baseline={comparison.baseline_coverage:.4f} candidate={comparison.candidate_coverage:.4f} delta={comparison.coverage_delta:.4f}',
            ]
        )

    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description='Compare two representative AutoRAG runs.')
    parser.add_argument(
        '--cases-path',
        type=Path,
        default=Path(__file__).with_name('representative_cases.json'),
        help='Path to the representative case manifest.',
    )
    parser.add_argument(
        '--baseline-output-dir',
        type=Path,
        required=True,
        help='Directory containing the baseline AutoRAG CSV outputs.',
    )
    parser.add_argument(
        '--candidate-output-dir',
        type=Path,
        required=True,
        help='Directory containing the candidate AutoRAG CSV outputs.',
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('/app/data/autorag/representative'),
        help='Directory where comparison artifacts will be written.',
    )
    parser.add_argument(
        '--run-id',
        type=str,
        default='representative_compare',
        help='Label used in the generated report filename.',
    )
    args = parser.parse_args()

    cases = load_cases(args.cases_path)
    baseline_outputs = load_run_outputs(args.baseline_output_dir)
    candidate_outputs = load_run_outputs(args.candidate_output_dir)
    comparisons = build_case_comparisons(cases, baseline_outputs, candidate_outputs)
    summary = build_summary(cases, baseline_outputs, candidate_outputs, comparisons)
    report_text = format_markdown(summary, comparisons, args.baseline_output_dir.name, args.candidate_output_dir.name)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / f'representative_comparison_{args.run_id}.md'
    table_path = args.output_dir / f'representative_comparison_{args.run_id}.csv'

    pd.DataFrame([asdict(comparison) for comparison in comparisons]).to_csv(table_path, index=False)
    report_path.write_text(report_text, encoding='utf-8')

    print(f'Saved comparison report: {report_path}')
    print(f'Saved comparison table: {table_path}')


if __name__ == '__main__':
    main()

