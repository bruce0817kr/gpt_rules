from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.schemas import ChatFeedbackRequest, ChatFeedbackResponse, ChatRequest, ChatResponse


class ChatFeedbackStore:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.interactions_path = self.root_dir / "chat_interactions.jsonl"
        self.feedback_path = self.root_dir / "chat_feedback.jsonl"
        self._lock = threading.Lock()

    def record_interaction(
        self,
        *,
        request: ChatRequest,
        response: ChatResponse,
        template_id: str | None,
        llm_used: bool,
    ) -> None:
        payload = {
            "response_id": response.response_id,
            "generated_at": response.generated_at.isoformat(),
            "request": request.model_dump(mode="json"),
            "response": response.model_dump(mode="json"),
            "template_id": template_id,
            "llm_used": llm_used,
        }
        self._append_jsonl(self.interactions_path, payload)

    def record_feedback(self, request: ChatFeedbackRequest) -> ChatFeedbackResponse:
        interaction = self.find_interaction(request.response_id)
        if interaction is None:
            raise KeyError(request.response_id)

        previous = self.latest_feedback(request.response_id)
        recorded_at = datetime.now(timezone.utc)
        feedback_id = uuid.uuid4().hex
        payload = {
            "feedback_id": feedback_id,
            "response_id": request.response_id,
            "rating": request.rating.value,
            "reason_codes": [reason.value for reason in request.reason_codes],
            "recorded_at": recorded_at.isoformat(),
            "question": interaction["request"].get("question", ""),
            "answer_mode": interaction["request"].get("answer_mode", ""),
        }
        self._append_jsonl(self.feedback_path, payload)
        return ChatFeedbackResponse(
            feedback_id=feedback_id,
            response_id=request.response_id,
            rating=request.rating,
            reason_codes=request.reason_codes,
            recorded_at=recorded_at,
            superseded_feedback_id=(str(previous.get("feedback_id", "")) or None) if previous else None,
        )

    def find_interaction(self, response_id: str) -> dict[str, Any] | None:
        for row in reversed(self._read_jsonl(self.interactions_path)):
            if str(row.get("response_id", "")) == response_id:
                return row
        return None

    def latest_feedback(self, response_id: str) -> dict[str, Any] | None:
        for row in reversed(self._read_jsonl(self.feedback_path)):
            if str(row.get("response_id", "")) == response_id:
                return row
        return None

    def _append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        with self._lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False))
                handle.write("\n")

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []

        rows: list[dict[str, Any]] = []
        with self._lock:
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                rows.append(json.loads(stripped))
        return rows
