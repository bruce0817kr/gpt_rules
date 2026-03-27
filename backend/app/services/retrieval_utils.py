from __future__ import annotations

from collections import defaultdict
import re

from app.models.schemas import AggregatedParentHit, ChunkSourceType, DocumentRecord
from app.services.vector_store import SearchHit


ENUMERATION_KEYWORDS = (
    '직급별',
    '급여별',
    '구분',
    '목록',
    '표',
    '종류',
    '유형',
    '필요건수',
    '필요 횟수',
    '수집',
    '전체',
    '모두',
)

WIDE_CANDIDATE_KEYWORDS = (
    '법인카드',
    '비교견적',
    '입찰',
    '수의계약',
    '출장비',
    '지급계',
    '차량관리',
    '차량 운행',
)

WIDE_TOP_K_KEYWORDS = (
    '법인카드',
    '출장비',
    '지급계',
    '차량관리',
    '차량 운행',
)

TARGETED_EXPANSION_GROUPS = (
    ('사업비', '증빙'),
    ('정산', '증빙'),
    ('교육훈련', '계획'),
    ('계약변경', '절차'),
    ('결과보고', '제출'),
)

WEAK_SNIPPET_PREFIXES = (
    '부칙',
    '※ 비고',
    '[시행',
)


def normalize_question_text(value: str) -> str:
    return re.sub(r'\s+', '', value).lower()


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


def _path_terms(value: str) -> list[str]:
    terms = [normalize_question_text(term) for term in re.split(r'[>/\s|·]+', value) if term]
    return [term for term in terms if len(term) >= 2]


def path_matches_question(question: str, path_key: str | None) -> bool:
    if not path_key:
        return False

    normalized_question = normalize_question_text(question)
    return any(term in normalized_question for term in _path_terms(path_key))


def _is_weak_child(hit: SearchHit) -> bool:
    return snippet_is_weak(hit.snippet) or hit.is_addendum or hit.is_appendix


def _parent_group_key(hit: SearchHit) -> str:
    if hit.parent_id:
        return hit.parent_id
    return f'{hit.document_id}::{hit.path_key or hit.location}'


def _representative_hit(hits: list[SearchHit], question: str) -> SearchHit:
    return max(
        hits,
        key=lambda hit: (
            not _is_weak_child(hit),
            title_matches_question(question, hit.title),
            path_matches_question(question, hit.path_key or hit.location),
            hit.score,
            -hit.chunk_index,
        ),
    )


def _source_type_for_group(hits: list[SearchHit]) -> ChunkSourceType:
    for hit in hits:
        if hit.source_type is not None:
            return hit.source_type
    return ChunkSourceType.METADATA


def _score_parent_group(hits: list[SearchHit], question: str, *, total_hits: int) -> AggregatedParentHit:
    representative_hit = _representative_hit(hits, question)
    best_child_score = max(hit.score for hit in hits)
    child_hit_count = len(hits)
    weak_child_count = sum(1 for hit in hits if _is_weak_child(hit))
    weak_ratio = weak_child_count / child_hit_count if child_hit_count else 0.0
    concentration = child_hit_count / total_hits if total_hits else 0.0

    title_signal = 0.15 if any(title_matches_question(question, hit.title) for hit in hits) else 0.0
    path_signal = 0.12 if any(path_matches_question(question, hit.path_key or hit.location) for hit in hits) else 0.0
    weak_penalty = 0.45 * (weak_ratio**2) + 0.05 * weak_ratio
    lexical_score = max(0.0, min(1.0, best_child_score + title_signal + path_signal - weak_penalty))

    concentration_bonus = 0.0
    if child_hit_count > 1:
        concentration_bonus = (0.10 * concentration) * (1.0 - (0.5 * weak_ratio))
    aggregate_score = max(0.0, min(1.0, lexical_score + concentration_bonus))

    return AggregatedParentHit(
        parent_id=_parent_group_key(representative_hit),
        document_id=representative_hit.document_id,
        document_title=representative_hit.title,
        source_type=_source_type_for_group(hits),
        path_key=representative_hit.path_key or representative_hit.location,
        location=representative_hit.location,
        representative_text=representative_hit.snippet,
        child_hit_count=child_hit_count,
        best_child_score=best_child_score,
        lexical_score=lexical_score,
        aggregate_score=aggregate_score,
        is_addendum=any(hit.is_addendum for hit in hits),
        is_appendix=any(hit.is_appendix for hit in hits),
    )


def aggregate_parent_hits(hits: list[SearchHit], question: str) -> list[AggregatedParentHit]:
    if not hits:
        return []

    grouped_hits: dict[str, list[SearchHit]] = defaultdict(list)
    for hit in hits:
        grouped_hits[_parent_group_key(hit)].append(hit)

    aggregated_hits = [
        _score_parent_group(group_hits, question, total_hits=len(hits))
        for group_hits in grouped_hits.values()
    ]
    return sorted(
        aggregated_hits,
        key=lambda hit: (
            -hit.aggregate_score,
            -hit.lexical_score,
            -hit.best_child_score,
            -hit.child_hit_count,
            hit.parent_id,
        ),
    )


def prioritize_hits(hits: list[SearchHit], question: str) -> list[SearchHit]:
    return sorted(
        hits,
        key=lambda hit: (
            0 if title_matches_question(question, hit.title) else 1,
            1 if snippet_is_weak(hit.snippet) else 0,
            -hit.score,
        ),
    )



def _tokenize_search_terms(value: str) -> list[str]:
    normalized = value.lower()
    tokens: list[str] = []
    current: list[str] = []
    for char in normalized:
        if char.isalnum():
            current.append(char)
            continue
        if len(current) >= 2:
            tokens.append(''.join(current))
        current = []
    if len(current) >= 2:
        tokens.append(''.join(current))
    return tokens



def score_document_title_match(question: str, title: str) -> float:
    question_tokens = set(_tokenize_search_terms(question))
    title_tokens = set(_tokenize_search_terms(title))
    if not question_tokens or not title_tokens:
        return 0.0

    overlap = question_tokens & title_tokens
    token_score = len(overlap) / len(title_tokens)
    normalized_question = normalize_question_text(question)
    normalized_title = normalize_question_text(title)
    prefix_bonus = 0.35 if any(question_token.startswith(title_token) for question_token in question_tokens for title_token in title_tokens) else 0.0
    substring_bonus = 0.35 if normalized_title and normalized_title in normalized_question else 0.0
    return min(1.0, token_score + max(prefix_bonus, substring_bonus))



def shortlist_documents_by_title(
    question: str,
    records: list[DocumentRecord],
    *,
    limit: int = 5,
    min_score: float = 0.25,
) -> list[DocumentRecord]:
    scored = [
        (score_document_title_match(question, record.title), record)
        for record in records
    ]
    shortlisted = [
        record
        for score, record in sorted(scored, key=lambda item: item[0], reverse=True)
        if score >= min_score
    ]
    return shortlisted[:limit]

