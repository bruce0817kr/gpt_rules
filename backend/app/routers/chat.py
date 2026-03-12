from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_chat_service, get_feedback_store
from app.models.schemas import ChatFeedbackRequest, ChatFeedbackResponse, ChatRequest, ChatResponse
from app.services.chat import ChatService
from app.services.feedback_store import ChatFeedbackStore

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    return await service.answer(request)


@router.post("/chat-feedback", response_model=ChatFeedbackResponse)
async def chat_feedback(
    request: ChatFeedbackRequest,
    store: ChatFeedbackStore = Depends(get_feedback_store),
) -> ChatFeedbackResponse:
    try:
        return store.record_feedback(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown response_id: {request.response_id}") from exc
