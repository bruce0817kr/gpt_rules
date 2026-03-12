from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def load_feedback_utils_module():
    module_path = Path(__file__).parent / "autorag" / "feedback_dataset_utils.py"
    spec = importlib.util.spec_from_file_location("autorag_feedback_dataset_utils", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(module_path.parent))
    spec.loader.exec_module(module)
    return module


def test_merge_feedback_records_uses_latest_feedback_within_window() -> None:
    module = load_feedback_utils_module()
    now = datetime.now(timezone.utc)
    interactions = [
        {
            "response_id": "response-1",
            "generated_at": now.isoformat(),
            "request": {
                "question": "비교견적 기준이 뭐야",
                "answer_mode": "procurement_bid",
                "categories": ["rule", "guide"],
                "top_k": 5,
            },
            "response": {
                "answer": "비교견적이 필요합니다.",
                "citations": [],
                "confidence": "medium",
            },
            "template_id": None,
            "llm_used": True,
        }
    ]
    feedback_events = [
        {
            "feedback_id": "old",
            "response_id": "response-1",
            "rating": "bad",
            "reason_codes": ["grounding_weak"],
            "recorded_at": (now - timedelta(days=2)).isoformat(),
        },
        {
            "feedback_id": "new",
            "response_id": "response-1",
            "rating": "bad",
            "reason_codes": ["answer_incorrect", "citation_mismatch"],
            "recorded_at": (now - timedelta(hours=1)).isoformat(),
        },
    ]

    merged = module.merge_feedback_records(
        interactions,
        feedback_events,
        since=now - timedelta(days=3),
    )

    assert len(merged) == 1
    assert merged[0]["feedback_id"] == "new"
    assert merged[0]["reason_codes"] == ["answer_incorrect", "citation_mismatch"]


def test_build_feedback_review_row_carries_reason_codes_and_duplicates() -> None:
    module = load_feedback_utils_module()
    row = module.build_feedback_review_row(
        {
            "response_id": "response-2",
            "feedback_id": "feedback-2",
            "recorded_at": "2026-03-12T00:00:00+00:00",
            "rating": "bad",
            "reason_codes": ["grounding_weak", "missing_detail"],
            "question": "계약 변경 승인 서류는 뭐야",
            "answer_mode": "contract_review",
            "categories": ["rule"],
            "answer": "서류를 확인하세요.",
            "citations": [],
        },
        duplicate_count=3,
    )

    assert row["candidate_source"] == "user_feedback"
    assert row["feedback_reason_codes"] == ["grounding_weak", "missing_detail"]
    assert row["feedback_duplicate_count"] == 3
    assert "duplicate_bad_count=3" in row["review_notes"]


def test_template_and_question_counts_group_records() -> None:
    module = load_feedback_utils_module()
    rows = [
        {
            "question": "법인카드 증빙 기준 알려줘",
            "question_normalized": "법인카드 증빙 기준 알려줘",
            "template_id": "corp_card_policy",
        },
        {
            "question": "법인카드 증빙 기준 알려줘?",
            "question_normalized": "법인카드 증빙 기준 알려줘",
            "template_id": "corp_card_policy",
        },
        {
            "question": "비교견적 제출 서류가 뭐야",
            "question_normalized": "비교견적 제출 서류가 뭐야",
            "template_id": "",
        },
    ]

    template_counts = module.template_id_counts(rows)
    question_counts = module.normalized_question_counts(rows)

    assert template_counts == [("corp_card_policy", 2), ("none", 1)]
    assert question_counts == [("법인카드 증빙 기준 알려줘", 2), ("비교견적 제출 서류가 뭐야", 1)]
