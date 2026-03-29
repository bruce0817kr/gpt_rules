from __future__ import annotations

import argparse
import sys
import asyncio
import json
import os
from pathlib import Path

import pandas as pd

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.dependencies import get_chat_service
from app.models.schemas import AnswerMode, ChatRequest, DocumentCategory


def apply_openrouter_env_fallback() -> None:
    if not os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENROUTER_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    if not os.environ.get("OPENAI_BASE_URL") and os.environ.get("OPENROUTER_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = os.environ["OPENROUTER_BASE_URL"]
    if not os.environ.get("LLM_MODEL") and os.environ.get("OPENROUTER_MODEL"):
        os.environ["LLM_MODEL"] = os.environ["OPENROUTER_MODEL"]


def load_cases(path: Path, split: str | None = None) -> list[dict]:
    payload = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(payload, list):
        raise ValueError(f'Representative case manifest must be a JSON list: {path}')
    if split is None or split == 'all':
        return payload
    return [case for case in payload if str(case.get('split', '')).strip() == split]


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


def main() -> None:
    apply_openrouter_env_fallback()
    parser = argparse.ArgumentParser(description='Run representative cases against the live backend and save lightweight comparison artifacts.')
    parser.add_argument('--cases-path', type=Path, default=Path(__file__).with_name('representative_cases.json'))
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--split', choices=['all', 'dev', 'validation', 'holdout'], default='all')
    args = parser.parse_args()

    cases = load_cases(args.cases_path, args.split)
    if not cases:
        raise ValueError(f'No representative cases matched split={args.split!r}')
    retrieval_on_df, retrieval_off_df, generation_df = asyncio.run(run_cases(cases))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    retrieval_on_df.to_csv(args.output_dir / 'retrieval_eval_reranker_on.csv', index=False)
    retrieval_off_df.to_csv(args.output_dir / 'retrieval_eval_reranker_off.csv', index=False)
    generation_df.to_csv(args.output_dir / 'generation_eval.csv', index=False)

    print(f'Saved lightweight representative snapshot to {args.output_dir} (split={args.split}, cases={len(cases)})')


if __name__ == '__main__':
    main()
