from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Iterable


def flatten_retrieval_gt(retrieval_gt: object) -> list[str]:
    flattened: list[str] = []
    seen: set[str] = set()

    if isinstance(retrieval_gt, list):
        for item in retrieval_gt:
            if isinstance(item, list):
                values = item
            else:
                values = [item]
            for value in values:
                normalized = str(value).strip()
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                flattened.append(normalized)
    else:
        normalized = str(retrieval_gt).strip()
        if normalized:
            flattened.append(normalized)

    return flattened


def retrieval_overlap_metrics(expected_ids: Iterable[str], actual_ids: Iterable[str]) -> dict[str, float]:
    expected = {str(value).strip() for value in expected_ids if str(value).strip()}
    actual = {str(value).strip() for value in actual_ids if str(value).strip()}
    overlap = expected & actual

    precision = len(overlap) / len(actual) if actual else 0.0
    recall = len(overlap) / len(expected) if expected else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision and recall else 0.0

    return {
        "expected_count": float(len(expected)),
        "actual_count": float(len(actual)),
        "overlap_count": float(len(overlap)),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def extract_answer_references(answer: str) -> list[int]:
    seen: set[int] = set()
    references: list[int] = []
    for match in re.finditer(r"\[(\d+)\]", answer):
        index = int(match.group(1))
        if index in seen:
            continue
        seen.add(index)
        references.append(index)
    return references


def citation_panel_is_clean(answer: str, citation_count: int) -> bool:
    references = extract_answer_references(answer)
    if not references:
        return citation_count == 0
    return references == list(range(1, len(references) + 1)) and len(references) == citation_count


def answer_similarity_score(current_answer: str, baseline_answer: str) -> float:
    current = normalize_answer_text(current_answer)
    baseline = normalize_answer_text(baseline_answer)
    if not current or not baseline:
        return 0.0
    return round(SequenceMatcher(a=current, b=baseline).ratio(), 4)


def normalize_answer_text(answer: str) -> str:
    return re.sub(r"\s+", " ", answer).strip().lower()


def classify_regression_status(
    *,
    retrieval_f1: float,
    answer_similarity: float,
    citation_panel_clean: bool,
    citation_count: int,
) -> str:
    if citation_count == 0 or not citation_panel_clean:
        return "high_risk"
    if retrieval_f1 < 0.5 or answer_similarity < 0.45:
        return "high_risk"
    if retrieval_f1 < 0.8 or answer_similarity < 0.65:
        return "needs_review"
    return "ok"
