from __future__ import annotations

import re

from app.services.vector_store import SearchHit


ENUMERATION_KEYWORDS = (
    "직급별",
    "등급별",
    "구분",
    "목록",
    "표",
    "종류",
    "유형",
    "필요인수",
    "필요 일수",
    "승진",
    "전체",
    "모두",
)

WIDE_CANDIDATE_KEYWORDS = (
    "법인카드",
    "비교견적",
    "입찰",
    "수의계약",
    "출장비",
    "징계",
    "차량관리",
    "차량 운행",
)

WIDE_TOP_K_KEYWORDS = (
    "법인카드",
    "출장비",
    "징계",
    "차량관리",
    "차량 운행",
)

TARGETED_EXPANSION_GROUPS = (
    ("사업비", "증빙"),
    ("정산", "증빙"),
    ("교육훈련", "계획"),
    ("계약변경", "서류"),
    ("결과보고", "제출"),
)

WEAK_SNIPPET_PREFIXES = (
    "부칙",
    "※ 비고",
    "[시행",
)


def normalize_question_text(value: str) -> str:
    return re.sub(r"\s+", "", value).lower()


def is_enumeration_query(question: str) -> bool:
    return any(keyword in question for keyword in ENUMERATION_KEYWORDS)


def needs_wide_candidate_search(question: str) -> bool:
    normalized = normalize_question_text(question)
    return any(normalize_question_text(keyword) in normalized for keyword in WIDE_CANDIDATE_KEYWORDS)


def needs_wide_top_k(question: str) -> bool:
    normalized = normalize_question_text(question)
    return any(normalize_question_text(keyword) in normalized for keyword in WIDE_TOP_K_KEYWORDS)


def needs_targeted_expansion(question: str) -> bool:
    normalized = normalize_question_text(question)
    return any(all(normalize_question_text(token) in normalized for token in tokens) for tokens in TARGETED_EXPANSION_GROUPS)


def retrieval_window(question: str, *, top_k: int, rerank_candidates: int) -> tuple[int, int]:
    enumeration_query = is_enumeration_query(question)
    targeted_expansion = needs_targeted_expansion(question)
    wide_top_k = needs_wide_top_k(question)
    wide_candidates = needs_wide_candidate_search(question)

    effective_top_k = max(top_k, 8) if enumeration_query or wide_top_k else top_k
    if targeted_expansion:
        effective_top_k = max(effective_top_k, 10)

    candidate_count = max(effective_top_k * 2, rerank_candidates)

    if enumeration_query:
        candidate_count = max(candidate_count, 18)
    if wide_candidates:
        candidate_count = max(candidate_count, 30)
    if targeted_expansion:
        candidate_count = max(candidate_count, 24)

    return effective_top_k, candidate_count


def deduplicate_hits(hits: list[SearchHit]) -> list[SearchHit]:
    unique_hits: list[SearchHit] = []
    seen_keys: set[tuple[str, str]] = set()

    for hit in hits:
        key = (hit.document_id, hit.location)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_hits.append(hit)

    return unique_hits


def snippet_is_weak(snippet: str) -> bool:
    normalized = snippet.strip()
    if not normalized:
        return True
    return any(normalized.startswith(prefix) for prefix in WEAK_SNIPPET_PREFIXES)


def title_matches_question(question: str, title: str) -> bool:
    normalized_question = normalize_question_text(question)
    normalized_title = normalize_question_text(title)
    if not normalized_title:
        return False
    return normalized_title in normalized_question


def prioritize_hits(hits: list[SearchHit], question: str) -> list[SearchHit]:
    return sorted(
        hits,
        key=lambda hit: (
            0 if title_matches_question(question, hit.title) else 1,
            1 if snippet_is_weak(hit.snippet) else 0,
            -hit.score,
        ),
    )
