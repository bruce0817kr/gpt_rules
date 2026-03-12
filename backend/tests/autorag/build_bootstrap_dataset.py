from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import pandas as pd

from app.dependencies import get_catalog, get_chat_service, get_parser
from app.models.schemas import AnswerMode, ChatRequest, DocumentCategory


def make_chunk_id(document_id: str, location: str) -> str:
    return f"{document_id}::{location}"


def load_seed_cases(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_corpus_rows() -> list[dict]:
    catalog = get_catalog()
    parser = get_parser()
    rows: list[dict] = []

    for record in catalog.list_documents():
        if record.status.value != "ready":
            continue

        try:
            sections = parser.parse(Path(record.file_path))
        except Exception:
            continue

        chunk_ids = [make_chunk_id(record.id, section.location) for section in sections]
        for index, section in enumerate(sections):
            rows.append(
                {
                    "doc_id": chunk_ids[index],
                    "contents": section.text,
                    "path": record.file_path,
                    "start_end_idx": (index, index),
                    "metadata": {
                        "last_modified_datetime": record.updated_at,
                        "page": section.page_number or -1,
                        "title": record.title,
                        "filename": record.filename,
                        "category": record.category.value,
                        "document_id": record.id,
                        "location": section.location,
                        "prev_id": chunk_ids[index - 1] if index > 0 else None,
                        "next_id": chunk_ids[index + 1] if index + 1 < len(chunk_ids) else None,
                    },
                }
            )

    return rows


async def build_qa_rows(seed_cases: list[dict]) -> list[dict]:
    service = get_chat_service()
    rows: list[dict] = []

    for case in seed_cases:
        categories = [DocumentCategory(value) for value in case.get("categories", [])]
        answer_mode = AnswerMode(case.get("answer_mode", "standard"))
        response = await service.answer(
            ChatRequest(
                question=case["question"],
                categories=categories,
                answer_mode=answer_mode,
            )
        )

        retrieval_gt = [
            [make_chunk_id(citation.document_id, citation.location)]
            for citation in response.citations
        ]
        unique_retrieval_gt: list[list[str]] = []
        seen_retrieval_gt: set[tuple[str, ...]] = set()
        for group in retrieval_gt:
            key = tuple(group)
            if key in seen_retrieval_gt:
                continue
            seen_retrieval_gt.add(key)
            unique_retrieval_gt.append(group)
        rows.append(
            {
                "qid": case["id"],
                "query": case["question"],
                "retrieval_gt": unique_retrieval_gt,
                "generation_gt": [response.answer],
                "answer_mode": answer_mode.value,
                "categories": [category.value for category in categories],
                "bootstrap_source": "current_system",
            }
        )

    return rows


async def main() -> None:
    parser = argparse.ArgumentParser(description="Build bootstrap AutoRAG datasets from the current RAG system.")
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path(__file__).with_name("seed_questions.json"),
        help="Path to the seed question JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/app/data/autorag/bootstrap"),
        help="Directory where corpus.parquet and qa.parquet will be written.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    corpus_rows = build_corpus_rows()
    qa_rows = await build_qa_rows(load_seed_cases(args.cases))

    corpus_df = pd.DataFrame(corpus_rows).reset_index(drop=True)
    qa_df = pd.DataFrame(qa_rows).reset_index(drop=True)

    corpus_df.to_parquet(args.output_dir / "corpus.parquet", index=False)
    qa_df.to_parquet(args.output_dir / "qa.parquet", index=False)
    (args.output_dir / "seed_cases_used.json").write_text(
        json.dumps(load_seed_cases(args.cases), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Saved corpus rows: {len(corpus_df)}")
    print(f"Saved qa rows: {len(qa_df)}")
    print(f"Output directory: {args.output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
