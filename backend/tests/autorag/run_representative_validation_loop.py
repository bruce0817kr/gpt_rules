from __future__ import annotations

import argparse
import sys
import asyncio
import json
from pathlib import Path

import pandas as pd

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.schemas import AnswerMode, ChatRequest, DocumentCategory
from app.dependencies import get_chat_service
from compare_representative_runs import load_cases
from evaluate_representative_gate import compute_gate_metrics, evaluate_gate, format_decision


def load_split_cases(path: Path, split: str) -> list[dict]:
    cases = load_cases(path)
    if split == 'all':
        return cases
    filtered = [case for case in cases if str(case.get('split', '')).strip() == split]
    if not filtered:
        raise ValueError(f'No cases found for split={split!r}')
    return filtered


async def run_cases(cases: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    service = get_chat_service()
    generation_rows = []
    retrieval_rows = []

    for case in cases:
        response = await service.answer(
            ChatRequest(
                question=case['question'],
                categories=[DocumentCategory(value) for value in case.get('categories', [])],
                answer_mode=AnswerMode(case['answer_mode']),
            )
        )
        generation_rows.append(
            {
                'qid': case['id'],
                'generated_texts': response.answer,
                'bleu': 0.0,
                'rouge': 0.0,
                'confidence': response.confidence,
                'retrieved_chunks': response.retrieved_chunks,
            }
        )
        retrieval_rows.append(
            {
                'qid': case['id'],
                'retrieval_f1': 0.0,
                'retrieval_recall': 0.0,
                'retrieval_precision': 0.0,
                'citation_count': len(response.citations),
                'confidence': response.confidence,
                'retrieved_chunks': response.retrieved_chunks,
            }
        )

    retrieval_df = pd.DataFrame(retrieval_rows)
    generation_df = pd.DataFrame(generation_rows)
    return retrieval_df.copy(), retrieval_df.copy(), generation_df


def save_snapshot(output_dir: Path, retrieval_on_df: pd.DataFrame, retrieval_off_df: pd.DataFrame, generation_df: pd.DataFrame) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    retrieval_on_df.to_csv(output_dir / 'retrieval_eval_reranker_on.csv', index=False)
    retrieval_off_df.to_csv(output_dir / 'retrieval_eval_reranker_off.csv', index=False)
    generation_df.to_csv(output_dir / 'generation_eval.csv', index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run a representative candidate snapshot and evaluate the split gate against an existing baseline snapshot.')
    parser.add_argument('--cases-path', type=Path, default=Path(__file__).with_name('representative_cases.json'))
    parser.add_argument('--split', choices=['dev', 'validation', 'holdout'], default='validation')
    parser.add_argument('--baseline-output-dir', type=Path, required=True)
    parser.add_argument('--candidate-output-dir', type=Path, required=True)
    parser.add_argument('--gate-output-dir', type=Path, required=True)
    parser.add_argument('--run-id', type=str, default='loop')
    args = parser.parse_args()

    cases = load_split_cases(args.cases_path, args.split)
    retrieval_on_df, retrieval_off_df, generation_df = asyncio.run(run_cases(cases))
    save_snapshot(args.candidate_output_dir, retrieval_on_df, retrieval_off_df, generation_df)

    baseline_outputs = {
        'retrieval_on': pd.read_csv(args.baseline_output_dir / 'retrieval_eval_reranker_on.csv'),
        'retrieval_off': pd.read_csv(args.baseline_output_dir / 'retrieval_eval_reranker_off.csv'),
        'generation': pd.read_csv(args.baseline_output_dir / 'generation_eval.csv'),
    }
    candidate_outputs = {
        'retrieval_on': retrieval_on_df,
        'retrieval_off': retrieval_off_df,
        'generation': generation_df,
    }
    metrics = compute_gate_metrics(cases, baseline_outputs, candidate_outputs, split='all')
    decision = evaluate_gate(metrics)

    args.gate_output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.gate_output_dir / f'representative_gate_{args.split}_{args.run_id}.md'
    json_path = args.gate_output_dir / f'representative_gate_{args.split}_{args.run_id}.json'
    report_path.write_text(format_decision(decision, args.baseline_output_dir.name, args.candidate_output_dir.name), encoding='utf-8')
    json_path.write_text(json.dumps({'passed': decision.passed, 'reasons': decision.reasons, 'metrics': metrics.__dict__}, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'{args.split} loop result: {"PASS" if decision.passed else "FAIL"}')
    print(f'candidate snapshot: {args.candidate_output_dir}')
    print(f'gate report: {report_path}')


if __name__ == '__main__':
    main()
