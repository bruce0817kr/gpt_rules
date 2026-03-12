from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from app.models.schemas import Citation
from gold_dataset_utils import build_retrieval_gt_from_citations, normalize_question


def parse_iso_datetime(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    return datetime.fromisoformat(normalized)


def load_jsonl_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        rows.append(json.loads(stripped))
    return rows


def latest_feedback_by_response(feedback_events: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for event in feedback_events:
        response_id = str(event.get("response_id", "")).strip()
        if not response_id:
            continue
        previous = latest.get(response_id)
        if previous is None:
            latest[response_id] = dict(event)
            continue
        if parse_iso_datetime(str(event.get("recorded_at", ""))) >= parse_iso_datetime(
            str(previous.get("recorded_at", ""))
        ):
            latest[response_id] = dict(event)
    return latest


def feedback_window_start(*, now: datetime, lookback_days: int) -> datetime:
    return now - timedelta(days=max(1, lookback_days))


def merge_feedback_records(
    interactions: Iterable[Mapping[str, Any]],
    feedback_events: Iterable[Mapping[str, Any]],
    *,
    since: datetime | None = None,
) -> list[dict[str, Any]]:
    interaction_map = {
        str(row.get("response_id", "")).strip(): dict(row)
        for row in interactions
        if str(row.get("response_id", "")).strip()
    }
    latest_feedback = latest_feedback_by_response(feedback_events)
    merged: list[dict[str, Any]] = []

    for response_id, feedback in latest_feedback.items():
        interaction = interaction_map.get(response_id)
        if interaction is None:
            continue

        recorded_at = parse_iso_datetime(str(feedback.get("recorded_at", "")))
        if since is not None and recorded_at < since:
            continue

        request = dict(interaction.get("request", {}))
        response = dict(interaction.get("response", {}))
        merged.append(
            {
                "response_id": response_id,
                "feedback_id": str(feedback.get("feedback_id", "")),
                "recorded_at": recorded_at.isoformat(),
                "rating": str(feedback.get("rating", "")).strip(),
                "reason_codes": list(feedback.get("reason_codes", [])),
                "generated_at": str(interaction.get("generated_at", "")),
                "question": str(request.get("question", "")).strip(),
                "question_normalized": normalize_question(str(request.get("question", ""))),
                "answer_mode": str(request.get("answer_mode", "")).strip(),
                "categories": list(request.get("categories", [])),
                "top_k": request.get("top_k"),
                "answer": str(response.get("answer", "")),
                "citations": list(response.get("citations", [])),
                "confidence": str(response.get("confidence", "")).strip(),
                "template_id": interaction.get("template_id"),
                "llm_used": bool(interaction.get("llm_used", False)),
            }
        )

    merged.sort(key=lambda row: row["recorded_at"], reverse=True)
    return merged


def build_feedback_review_row(record: Mapping[str, Any], *, duplicate_count: int = 1) -> dict[str, Any]:
    citations = [Citation.model_validate(citation) for citation in record.get("citations", [])]
    retrieval_gt = build_retrieval_gt_from_citations(citations)
    rating = str(record.get("rating", "")).strip()
    reason_codes = [str(reason).strip() for reason in record.get("reason_codes", []) if str(reason).strip()]

    review_notes = []
    review_notes.append(f"user_rating={rating}")
    if reason_codes:
        review_notes.append(f"user_reason_codes={','.join(reason_codes)}")
    if duplicate_count > 1:
        review_notes.append(f"duplicate_bad_count={duplicate_count}")

    return {
        "qid": str(record.get("response_id", "")),
        "query": str(record.get("question", "")),
        "answer_mode": str(record.get("answer_mode", "")),
        "categories": list(record.get("categories", [])),
        "persona_id": "",
        "persona_label": "",
        "candidate_note": ",".join(reason_codes),
        "candidate_source": "user_feedback",
        "feedback_id": str(record.get("feedback_id", "")),
        "feedback_label": rating,
        "feedback_recorded_at": str(record.get("recorded_at", "")),
        "feedback_duplicate_count": duplicate_count,
        "feedback_reason_codes": reason_codes,
        "bootstrap_generation_gt": [str(record.get("answer", ""))],
        "bootstrap_retrieval_gt": retrieval_gt,
        "reviewed_generation_gt": [],
        "reviewed_retrieval_gt": [],
        "bootstrap_citations": [citation.model_dump(mode="json") for citation in citations],
        "review_status": "pending",
        "review_notes": " | ".join(review_notes),
        "selected_for_gold": False,
    }


def dedupe_bad_feedback(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for record in records:
        normalized = str(record.get("question_normalized", "")).strip() or normalize_question(
            str(record.get("question", ""))
        )
        dedupe_key = normalized or str(record.get("response_id", "")).strip()
        if not dedupe_key:
            continue
        existing = deduped.get(dedupe_key)
        if existing is None:
            deduped[dedupe_key] = {
                **dict(record),
                "duplicate_bad_count": 1,
            }
            continue
        existing["duplicate_bad_count"] = int(existing.get("duplicate_bad_count", 1)) + 1
        if str(record.get("recorded_at", "")) > str(existing.get("recorded_at", "")):
            updated = {**dict(record), "duplicate_bad_count": existing["duplicate_bad_count"]}
            deduped[dedupe_key] = updated
    rows = list(deduped.values())
    rows.sort(key=lambda row: (int(row.get("duplicate_bad_count", 1)), str(row.get("recorded_at", ""))), reverse=True)
    return rows


def reason_code_counts(reason_groups: Iterable[Iterable[str]]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for reason_group in reason_groups:
        for reason_code in reason_group:
            normalized = str(reason_code).strip()
            if not normalized:
                continue
            counts[normalized] = counts.get(normalized, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def template_id_counts(records: Iterable[Mapping[str, Any]]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for record in records:
        template_id = str(record.get("template_id", "")).strip() or "none"
        counts[template_id] = counts.get(template_id, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def normalized_question_counts(records: Iterable[Mapping[str, Any]]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for record in records:
        question = str(record.get("question_normalized", "")).strip() or normalize_question(str(record.get("question", "")))
        if not question:
            continue
        counts[question] = counts.get(question, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
