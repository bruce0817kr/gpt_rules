from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from app.models.schemas import (
    AnswerMode,
    ChatFeedbackRequest,
    ChatRequest,
    ChatResponse,
    FeedbackLabel,
    FeedbackReasonCode,
)
from app.services.feedback_store import ChatFeedbackStore


def test_feedback_store_records_interaction_and_feedback(tmp_path: Path) -> None:
    store = ChatFeedbackStore(tmp_path / "feedback")
    request = ChatRequest(question="법인카드 증빙 기준을 알려줘", answer_mode=AnswerMode.AUDIT_RESPONSE)
    response = ChatResponse(
        response_id="response-1",
        generated_at=datetime.now(timezone.utc),
        answer="증빙 기준은 영수증과 사용 목적 확인입니다.",
        citations=[],
        confidence="medium",
        disclaimer="원문을 확인하세요.",
        retrieved_chunks=1,
    )

    store.record_interaction(request=request, response=response, template_id="corp_card_policy", llm_used=False)
    feedback = store.record_feedback(
        ChatFeedbackRequest(
            response_id="response-1",
            rating=FeedbackLabel.BAD,
            reason_codes=[FeedbackReasonCode.GROUNDING_WEAK, FeedbackReasonCode.CITATION_MISMATCH],
        )
    )

    assert feedback.response_id == "response-1"
    assert feedback.reason_codes == [
        FeedbackReasonCode.GROUNDING_WEAK,
        FeedbackReasonCode.CITATION_MISMATCH,
    ]
    assert store.find_interaction("response-1") is not None
    latest_feedback = store.latest_feedback("response-1")
    assert latest_feedback is not None
    assert latest_feedback["reason_codes"] == ["grounding_weak", "citation_mismatch"]


def test_bad_feedback_requires_reason_code() -> None:
    try:
        ChatFeedbackRequest(response_id="response-2", rating=FeedbackLabel.BAD, reason_codes=[])
    except ValidationError as exc:
        assert "reason code" in str(exc).lower()
    else:
        raise AssertionError("Expected bad feedback without reason codes to fail validation.")
