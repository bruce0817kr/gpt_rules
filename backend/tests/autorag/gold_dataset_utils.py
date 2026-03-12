from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

from app.models.schemas import AnswerMode, Citation, DocumentCategory

APPROVED_REVIEW_STATUSES = {"approved", "approved_with_edits"}
REVIEW_STATUS_PRIORITY = {
    "approved_with_edits": 3,
    "approved": 2,
    "pending": 1,
    "rejected": 0,
    "": 0,
}
REVIEW_SOURCE_PRIORITY = {
    "user_feedback": 2,
    "persona_agent": 1,
    "unknown": 0,
}

QUESTION_STOPWORDS = {
    "무엇인가요",
    "무엇인지",
    "무엇",
    "어떻게",
    "있나요",
    "있을까요",
    "있다면",
    "필요한",
    "필요",
    "반드시",
    "주요",
    "확인",
    "확인해야",
    "알려줘",
    "정리해줘",
    "정리",
    "기준",
    "절차",
    "항목",
    "목록",
    "서류",
    "제출",
    "과정",
    "형식",
    "때",
    "시",
    "전",
    "후",
    "및",
    "그",
    "이",
    "있는",
    "따라야",
    "따라",
    "인가요",
    "되나요",
}

ALLOWED_CATEGORIES_BY_MODE: dict[AnswerMode, set[str]] = {
    AnswerMode.STANDARD: {category.value for category in DocumentCategory},
    AnswerMode.HR_ADMIN: {
        DocumentCategory.RULE.value,
        DocumentCategory.GUIDE.value,
        DocumentCategory.LAW.value,
        DocumentCategory.NOTICE.value,
    },
    AnswerMode.CONTRACT_REVIEW: {
        DocumentCategory.RULE.value,
        DocumentCategory.GUIDE.value,
        DocumentCategory.LAW.value,
    },
    AnswerMode.PROJECT_MANAGEMENT: {
        DocumentCategory.RULE.value,
        DocumentCategory.GUIDE.value,
        DocumentCategory.NOTICE.value,
    },
    AnswerMode.PROCUREMENT_BID: {
        DocumentCategory.RULE.value,
        DocumentCategory.GUIDE.value,
        DocumentCategory.LAW.value,
        DocumentCategory.NOTICE.value,
    },
    AnswerMode.AUDIT_RESPONSE: {
        DocumentCategory.RULE.value,
        DocumentCategory.GUIDE.value,
        DocumentCategory.LAW.value,
        DocumentCategory.NOTICE.value,
    },
}


def load_json_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("cases"), list):
        return payload["cases"]
    raise ValueError(f"Unsupported case payload shape: {path}")


def normalize_question(question: str) -> str:
    collapsed = re.sub(r"\s+", " ", question).strip()
    return collapsed.rstrip(" ?.!")


def question_keywords(question: str) -> set[str]:
    normalized = normalize_question(question).lower()
    tokens = re.findall(r"[0-9a-z가-힣]+", normalized)
    return {
        token
        for token in tokens
        if len(token) >= 2 and token not in QUESTION_STOPWORDS
    }


def dedupe_string_list(values: Iterable[str]) -> list[str]:
    unique_values: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_values.append(normalized)
    return unique_values


def question_overlap_summary(
    question: str,
    *,
    answer_mode: str,
    other_questions: Iterable[Mapping[str, Any]],
    question_key: str = "question",
    mode_key: str = "answer_mode",
    id_key: str = "id",
) -> dict[str, Any] | None:
    base_keywords = question_keywords(question)
    best_match: dict[str, Any] | None = None

    for other in other_questions:
        other_question = normalize_question(str(other.get(question_key, "")))
        if not other_question:
            continue

        other_keywords = question_keywords(other_question)
        union = base_keywords | other_keywords
        jaccard = (len(base_keywords & other_keywords) / len(union)) if union else 0.0
        if str(other.get(mode_key, "")).strip() == answer_mode:
            jaccard += 0.05

        candidate = {
            "id": str(other.get(id_key, "")),
            "question": other_question,
            "answer_mode": str(other.get(mode_key, "")),
            "score": round(jaccard, 4),
            "shared_keywords": sorted(base_keywords & other_keywords),
        }
        if best_match is None or candidate["score"] > best_match["score"]:
            best_match = candidate

    return best_match


def suggest_review_action(seed_overlap: Mapping[str, Any] | None, peer_overlap: Mapping[str, Any] | None) -> str:
    seed_score = float(seed_overlap["score"]) if seed_overlap else 0.0
    peer_score = float(peer_overlap["score"]) if peer_overlap else 0.0

    if seed_score >= 0.55 or peer_score >= 0.65:
        return "merge_or_skip"
    if seed_score >= 0.35 or peer_score >= 0.45:
        return "review_edit"
    return "review_new"


def make_candidate_id(persona_id: str, answer_mode: str, index: int, question: str) -> str:
    digest = hashlib.sha1(normalize_question(question).encode("utf-8")).hexdigest()[:8]
    return f"{persona_id}_{answer_mode}_{index:02d}_{digest}"


def validate_candidate_case(case: Mapping[str, Any]) -> dict[str, Any]:
    persona_id = str(case.get("persona_id", "")).strip()
    persona_label = str(case.get("persona_label", "")).strip()
    question = normalize_question(str(case.get("question", "")))
    note = str(case.get("candidate_note", case.get("note", ""))).strip()
    answer_mode = AnswerMode(str(case.get("answer_mode", "")).strip())

    if len(question) < 8:
        raise ValueError("Candidate question is too short.")

    raw_categories = case.get("categories", [])
    if not isinstance(raw_categories, list):
        raise ValueError("Candidate categories must be a list.")

    categories = dedupe_string_list(DocumentCategory(str(category)).value for category in raw_categories)
    if not categories:
        raise ValueError("Candidate categories must not be empty.")

    allowed_categories = ALLOWED_CATEGORIES_BY_MODE[answer_mode]
    invalid_categories = [category for category in categories if category not in allowed_categories]
    if invalid_categories:
        raise ValueError(
            f"Invalid categories for {answer_mode.value}: {', '.join(invalid_categories)}"
        )

    return {
        "id": str(case.get("id", "")).strip(),
        "question": question,
        "answer_mode": answer_mode.value,
        "categories": categories,
        "persona_id": persona_id,
        "persona_label": persona_label,
        "candidate_note": note,
        "source": str(case.get("source", "persona_agent")).strip() or "persona_agent",
    }


def finalize_candidate_cases(
    cases: list[Mapping[str, Any]],
    *,
    existing_questions: Iterable[str],
) -> list[dict[str, Any]]:
    finalized: list[dict[str, Any]] = []
    seen_questions = {normalize_question(question) for question in existing_questions if str(question).strip()}

    counters: dict[str, int] = {}
    for raw_case in cases:
        case = validate_candidate_case(raw_case)
        normalized_question = normalize_question(case["question"])
        if normalized_question in seen_questions:
            continue
        seen_questions.add(normalized_question)

        mode = case["answer_mode"]
        counters[mode] = counters.get(mode, 0) + 1
        if not case["id"]:
            case["id"] = make_candidate_id(
                case["persona_id"] or "persona",
                mode,
                counters[mode],
                case["question"],
            )
        finalized.append(case)

    return finalized


def build_retrieval_gt_from_citations(citations: list[Citation]) -> list[list[str]]:
    unique_groups: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for citation in citations:
        group = [f"{citation.document_id}::{citation.location}"]
        key = tuple(group)
        if key in seen:
            continue
        seen.add(key)
        unique_groups.append(group)
    return unique_groups


def build_review_row(case: Mapping[str, Any], answer: str, citations: list[Citation]) -> dict[str, Any]:
    retrieval_gt = build_retrieval_gt_from_citations(citations)
    citation_rows = [citation.model_dump(mode="json") for citation in citations]
    return {
        "qid": case["id"],
        "query": case["question"],
        "answer_mode": case["answer_mode"],
        "categories": list(case["categories"]),
        "persona_id": case.get("persona_id", ""),
        "persona_label": case.get("persona_label", ""),
        "candidate_note": case.get("candidate_note", ""),
        "candidate_source": case.get("source", "persona_agent"),
        "bootstrap_generation_gt": [answer],
        "bootstrap_retrieval_gt": retrieval_gt,
        "reviewed_generation_gt": [answer],
        "reviewed_retrieval_gt": retrieval_gt,
        "bootstrap_citations": citation_rows,
        "review_status": "pending",
        "review_notes": "",
        "selected_for_gold": False,
    }


def extract_approved_gold_rows(review_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    approved_rows: list[dict[str, Any]] = []
    for row in review_rows:
        review_status = str(row.get("review_status", "")).strip().lower()
        selected_for_gold = bool(row.get("selected_for_gold", False))
        if review_status not in APPROVED_REVIEW_STATUSES and not selected_for_gold:
            continue

        generation_gt = row.get("reviewed_generation_gt", [])
        retrieval_gt = row.get("reviewed_retrieval_gt", [])
        if not generation_gt or not retrieval_gt:
            continue

        approved_rows.append(
            {
                "qid": str(row["qid"]),
                "query": str(row["query"]),
                "retrieval_gt": retrieval_gt,
                "generation_gt": generation_gt,
                "answer_mode": str(row["answer_mode"]),
                "categories": list(row.get("categories", [])),
                "gold_source": "review_queue",
                "persona_id": str(row.get("persona_id", "")),
            }
        )
    return approved_rows


def review_row_merge_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return (
        normalize_question(str(row.get("query", ""))),
        str(row.get("answer_mode", "")).strip(),
    )


def review_row_priority(row: Mapping[str, Any]) -> tuple[int, int, int, int, int, int, int]:
    review_status = str(row.get("review_status", "")).strip().lower()
    reviewed_generation_gt = row.get("reviewed_generation_gt", [])
    reviewed_retrieval_gt = row.get("reviewed_retrieval_gt", [])
    feedback_duplicate_count = int(row.get("feedback_duplicate_count", 0) or 0)
    review_notes = str(row.get("review_notes", "")).strip()

    return (
        1 if bool(row.get("selected_for_gold", False)) else 0,
        REVIEW_STATUS_PRIORITY.get(review_status, 0),
        1 if bool(reviewed_generation_gt) else 0,
        1 if bool(reviewed_retrieval_gt) else 0,
        feedback_duplicate_count,
        len(review_notes),
        len(str(row.get("candidate_note", "")).strip()),
    )


def merge_review_rows(review_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    merged_by_key: dict[tuple[str, str], dict[str, Any]] = {}

    for raw_row in review_rows:
        row = dict(raw_row)
        key = review_row_merge_key(row)
        if not key[0] or not key[1]:
            continue

        source = str(row.get("candidate_source", "")).strip() or "unknown"
        qid = str(row.get("qid", "")).strip()
        persona_id = str(row.get("persona_id", "")).strip()
        row["merged_qids"] = dedupe_string_list([qid])
        row["merged_sources"] = dedupe_string_list([source])
        row["merged_persona_ids"] = dedupe_string_list([persona_id])

        existing = merged_by_key.get(key)
        if existing is None:
            merged_by_key[key] = row
            continue

        preferred = row if review_row_priority(row) > review_row_priority(existing) else existing
        other = existing if preferred is row else row
        combined = dict(preferred)
        combined["merged_qids"] = dedupe_string_list(
            [*preferred.get("merged_qids", []), *other.get("merged_qids", [])]
        )
        combined["merged_sources"] = dedupe_string_list(
            [*preferred.get("merged_sources", []), *other.get("merged_sources", [])]
        )
        combined["merged_persona_ids"] = dedupe_string_list(
            [*preferred.get("merged_persona_ids", []), *other.get("merged_persona_ids", [])]
        )
        merged_by_key[key] = combined

    return sorted(
        merged_by_key.values(),
        key=lambda row: (str(row.get("answer_mode", "")), normalize_question(str(row.get("query", "")))),
    )


def review_backlog_snapshot(review_rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(review_rows)
    by_status = Counter(str(row.get("review_status", "")).strip().lower() or "unknown" for row in rows)
    by_source = Counter(str(row.get("candidate_source", "")).strip() or "unknown" for row in rows)
    by_answer_mode = Counter(str(row.get("answer_mode", "")).strip() or "unknown" for row in rows)
    by_persona = Counter(str(row.get("persona_id", "")).strip() or "unknown" for row in rows)

    gold_ready_rows = [
        row
        for row in rows
        if str(row.get("review_status", "")).strip().lower() in APPROVED_REVIEW_STATUSES
        or bool(row.get("selected_for_gold", False))
    ]

    return {
        "total_rows": len(rows),
        "pending_rows": by_status.get("pending", 0),
        "approved_rows": sum(by_status.get(status, 0) for status in APPROVED_REVIEW_STATUSES),
        "selected_for_gold_rows": sum(1 for row in rows if bool(row.get("selected_for_gold", False))),
        "gold_ready_rows": len(gold_ready_rows),
        "duplicate_clusters": sum(1 for row in rows if len(row.get("merged_qids", [])) > 1),
        "by_status": dict(sorted(by_status.items())),
        "by_source": dict(sorted(by_source.items())),
        "by_answer_mode": dict(sorted(by_answer_mode.items())),
        "by_persona": dict(sorted(by_persona.items())),
    }


def review_packet_priority(row: Mapping[str, Any]) -> tuple[int, int, int, int, int]:
    source = str(row.get("candidate_source", "")).strip() or "unknown"
    duplicate_count = int(row.get("feedback_duplicate_count", 0) or 0)
    merged_qid_count = len(row.get("merged_qids", []) or [])
    review_notes_length = len(str(row.get("review_notes", "")).strip())
    candidate_note_length = len(str(row.get("candidate_note", "")).strip())

    return (
        REVIEW_SOURCE_PRIORITY.get(source, 0),
        duplicate_count,
        merged_qid_count,
        review_notes_length,
        candidate_note_length,
    )


def build_balanced_review_packets(
    review_rows: Iterable[Mapping[str, Any]],
    *,
    packet_size: int = 12,
) -> list[dict[str, Any]]:
    if packet_size <= 0:
        raise ValueError("packet_size must be positive.")

    pending_rows = [
        dict(row)
        for row in review_rows
        if str(row.get("review_status", "")).strip().lower() == "pending"
    ]

    queues_by_mode: dict[str, list[dict[str, Any]]] = {}
    for row in pending_rows:
        answer_mode = str(row.get("answer_mode", "")).strip() or "unknown"
        queues_by_mode.setdefault(answer_mode, []).append(row)

    for answer_mode, mode_rows in queues_by_mode.items():
        queues_by_mode[answer_mode] = sorted(
            mode_rows,
            key=lambda row: (
                -review_packet_priority(row)[0],
                -review_packet_priority(row)[1],
                -review_packet_priority(row)[2],
                -review_packet_priority(row)[3],
                -review_packet_priority(row)[4],
                normalize_question(str(row.get("query", ""))),
            ),
        )

    packets: list[dict[str, Any]] = []
    packet_index = 1
    while any(queues_by_mode.values()):
        packet_rows: list[dict[str, Any]] = []
        while len(packet_rows) < packet_size and any(queues_by_mode.values()):
            active_modes = sorted(
                (
                    answer_mode
                    for answer_mode, rows in queues_by_mode.items()
                    if rows
                ),
                key=lambda answer_mode: (-len(queues_by_mode[answer_mode]), answer_mode),
            )
            for answer_mode in active_modes:
                if len(packet_rows) >= packet_size:
                    break
                packet_rows.append(queues_by_mode[answer_mode].pop(0))

        by_mode = Counter(str(row.get("answer_mode", "")).strip() or "unknown" for row in packet_rows)
        by_persona = Counter(str(row.get("persona_id", "")).strip() or "unknown" for row in packet_rows)
        packets.append(
            {
                "packet_index": packet_index,
                "row_count": len(packet_rows),
                "by_answer_mode": dict(sorted(by_mode.items())),
                "by_persona": dict(sorted(by_persona.items())),
                "rows": packet_rows,
            }
        )
        packet_index += 1

    return packets


def apply_review_decisions(
    review_rows: Iterable[Mapping[str, Any]],
    decisions: Mapping[str, Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    updated_rows: list[dict[str, Any]] = []
    touched_qids: list[str] = []

    for raw_row in review_rows:
        row = dict(raw_row)
        qid = str(row.get("qid", "")).strip()
        decision = decisions.get(qid)
        if not decision:
            updated_rows.append(row)
            continue

        row["review_status"] = str(decision.get("review_status", row.get("review_status", "pending"))).strip()
        row["selected_for_gold"] = bool(decision.get("selected_for_gold", row.get("selected_for_gold", False)))
        row["review_notes"] = str(decision.get("review_notes", row.get("review_notes", ""))).strip()

        if "reviewed_generation_gt" in decision:
            row["reviewed_generation_gt"] = list(decision.get("reviewed_generation_gt") or [])
        if "reviewed_retrieval_gt" in decision:
            row["reviewed_retrieval_gt"] = list(decision.get("reviewed_retrieval_gt") or [])

        updated_rows.append(row)
        touched_qids.append(qid)

    return updated_rows, touched_qids
