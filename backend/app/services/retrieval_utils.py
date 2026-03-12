from __future__ import annotations

from app.services.vector_store import SearchHit


ENUMERATION_KEYWORDS = (
    "직급별",
    "등급별",
    "구분",
    "목록",
    "표",
    "종류",
    "유형",
    "소요년수",
    "소요 연수",
    "승진",
    "전체",
    "모두",
)

WIDE_CANDIDATE_KEYWORDS = (
    "법인카드",
    "비교견적",
    "입찰",
    "수의계약",
)

WIDE_TOP_K_KEYWORDS = (
    "법인카드",
)

TARGETED_EXPANSION_GROUPS = (
    ("사업비", "증빙"),
    ("정산", "증빙"),
    ("교육훈련", "계획"),
    ("계약변경", "서류"),
    ("결과보고", "제출"),
)


def is_enumeration_query(question: str) -> bool:
    return any(keyword in question for keyword in ENUMERATION_KEYWORDS)


def needs_wide_candidate_search(question: str) -> bool:
    normalized = question.replace(" ", "")
    return any(keyword.replace(" ", "") in normalized for keyword in WIDE_CANDIDATE_KEYWORDS)


def needs_wide_top_k(question: str) -> bool:
    normalized = question.replace(" ", "")
    return any(keyword.replace(" ", "") in normalized for keyword in WIDE_TOP_K_KEYWORDS)


def needs_targeted_expansion(question: str) -> bool:
    normalized = question.replace(" ", "")
    return any(all(token in normalized for token in tokens) for tokens in TARGETED_EXPANSION_GROUPS)


def retrieval_window(question: str, *, top_k: int, rerank_candidates: int) -> tuple[int, int]:
    enumeration_query = is_enumeration_query(question)
    targeted_expansion = needs_targeted_expansion(question)
    effective_top_k = max(top_k, 8) if enumeration_query or needs_wide_top_k(question) else top_k
    if targeted_expansion:
        effective_top_k = max(effective_top_k, 10)
    candidate_count = max(effective_top_k * 2, rerank_candidates)

    if enumeration_query:
        candidate_count = max(candidate_count, 18)
    if needs_wide_candidate_search(question):
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
