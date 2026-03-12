from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import numpy as np
import pandas as pd
from autorag.evaluation import evaluate_generation, evaluate_retrieval
from autorag.schema.metricinput import MetricInput

from app.dependencies import get_chat_service, get_reranker, get_settings, get_vector_store
from app.models.schemas import AnswerMode, ChatRequest, DocumentCategory
from app.services.retrieval_utils import deduplicate_hits, retrieval_window


def make_chunk_id(document_id: str, location: str) -> str:
    return f"{document_id}::{location}"


def load_qa(qa_path: Path) -> pd.DataFrame:
    qa_df = pd.read_parquet(qa_path, engine="pyarrow").reset_index(drop=True)
    if qa_df["query"].duplicated().any():
        duplicated = qa_df.loc[qa_df["query"].duplicated(), "query"].tolist()
        raise ValueError(f"Queries must be unique for this evaluator: {duplicated}")
    return qa_df


def normalize_retrieval_gt(value: object) -> list[list[str]]:
    def dedupe_groups(groups: list[list[str]]) -> list[list[str]]:
        seen: set[tuple[str, ...]] = set()
        unique_groups: list[list[str]] = []
        for group in groups:
            key = tuple(group)
            if key in seen:
                continue
            seen.add(key)
            unique_groups.append(group)
        return unique_groups

    if isinstance(value, np.ndarray):
        value = value.tolist()

    if isinstance(value, list):
        if value and isinstance(value[0], (list, tuple, np.ndarray)):
            normalized_groups: list[list[str]] = []
            for group in value:
                if isinstance(group, np.ndarray):
                    group = group.tolist()
                if isinstance(group, (list, tuple)):
                    items = [str(item) for item in group if str(item).strip()]
                    if items:
                        normalized_groups.append(items)
            return dedupe_groups(normalized_groups)

        flat_items = [str(item) for item in value if str(item).strip()]
        return dedupe_groups([[item] for item in flat_items])

    normalized = str(value).strip()
    return [[normalized]] if normalized else []


def metric_inputs_for_retrieval(qa_df: pd.DataFrame) -> list[MetricInput]:
    return [
        MetricInput(query=row["query"], retrieval_gt=normalize_retrieval_gt(row["retrieval_gt"]))
        for _, row in qa_df.iterrows()
    ]


def metric_inputs_for_generation(qa_df: pd.DataFrame) -> list[MetricInput]:
    def normalize_generation_gt(value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        normalized = str(value).strip()
        return [normalized] if normalized else []

    return [
        MetricInput(query=row["query"], generation_gt=normalize_generation_gt(row["generation_gt"]))
        for _, row in qa_df.iterrows()
    ]


async def batch_generate(qa_df: pd.DataFrame, queries: list[str]) -> list[str]:
    service = get_chat_service()
    answers: list[str] = []
    lookup = qa_df.set_index("query").to_dict("index")

    for query in queries:
        row = lookup[query]
        response = await service.answer(
            ChatRequest(
                question=query,
                categories=[DocumentCategory(value) for value in row["categories"]],
                answer_mode=AnswerMode(row["answer_mode"]),
            )
        )
        answers.append(response.answer)

    return answers
def batch_retrieve(
    qa_df: pd.DataFrame,
    queries: list[str],
    *,
    use_reranker: bool,
) -> tuple[list[list[str]], list[list[str]], list[list[float]]]:
    settings = get_settings()
    vector_store = get_vector_store()
    reranker = get_reranker() if use_reranker else None
    lookup = qa_df.set_index("query").to_dict("index")

    retrieved_contents: list[list[str]] = []
    retrieved_ids: list[list[str]] = []
    retrieve_scores: list[list[float]] = []

    for query in queries:
        row = lookup[query]
        categories = [DocumentCategory(value) for value in row["categories"]]
        top_k, candidate_count = retrieval_window(
            query,
            top_k=settings.top_k,
            rerank_candidates=settings.rerank_candidates,
        )
        hits = vector_store.search(question=query, categories=categories, top_k=candidate_count)
        hits = deduplicate_hits(hits)
        if reranker is not None:
            hits = reranker.rerank(query, hits, top_k=top_k)
        else:
            hits = hits[:top_k]
        hits = deduplicate_hits(hits)
        retrieved_contents.append([hit.snippet for hit in hits])
        retrieved_ids.append([make_chunk_id(hit.document_id, hit.location) for hit in hits])
        retrieve_scores.append([float(hit.score) for hit in hits])

    return retrieved_contents, retrieved_ids, retrieve_scores


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the current RAG with AutoRAG decorators.")
    parser.add_argument(
        "--qa-path",
        type=Path,
        default=Path("/app/data/autorag/bootstrap/qa.parquet"),
        help="Path to qa.parquet.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/results"),
        help="Directory where evaluation CSVs will be written.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    qa_df = load_qa(args.qa_path)
    queries = qa_df["query"].tolist()

    @evaluate_retrieval(
        metric_inputs=metric_inputs_for_retrieval(qa_df),
        metrics=["retrieval_f1", "retrieval_recall", "retrieval_precision"],
    )
    def retrieval_with_reranker(query_batch: list[str]):
        return batch_retrieve(qa_df, query_batch, use_reranker=True)

    @evaluate_retrieval(
        metric_inputs=metric_inputs_for_retrieval(qa_df),
        metrics=["retrieval_f1", "retrieval_recall", "retrieval_precision"],
    )
    def retrieval_without_reranker(query_batch: list[str]):
        return batch_retrieve(qa_df, query_batch, use_reranker=False)

    @evaluate_generation(
        metric_inputs=metric_inputs_for_generation(qa_df),
        metrics=["bleu", "rouge"],
    )
    def current_generation(query_batch: list[str]):
        generated_texts = asyncio.run(batch_generate(qa_df, query_batch))
        return generated_texts, [[1]] * len(generated_texts), [[0.0]] * len(generated_texts)

    retrieval_rerank_df = retrieval_with_reranker(queries)
    retrieval_baseline_df = retrieval_without_reranker(queries)
    generation_df = current_generation(queries)

    retrieval_rerank_df.to_csv(args.output_dir / "retrieval_eval_reranker_on.csv", index=False)
    retrieval_baseline_df.to_csv(args.output_dir / "retrieval_eval_reranker_off.csv", index=False)
    generation_df.to_csv(args.output_dir / "generation_eval.csv", index=False)

    print("Saved:", args.output_dir / "retrieval_eval_reranker_on.csv")
    print("Saved:", args.output_dir / "retrieval_eval_reranker_off.csv")
    print("Saved:", args.output_dir / "generation_eval.csv")
    print("Retrieval mean (reranker on):")
    print(retrieval_rerank_df.mean(numeric_only=True).to_dict())
    print("Retrieval mean (reranker off):")
    print(retrieval_baseline_df.mean(numeric_only=True).to_dict())
    print("Generation mean:")
    print(generation_df.mean(numeric_only=True).to_dict())


if __name__ == "__main__":
    main()
