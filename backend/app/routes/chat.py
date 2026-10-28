from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import get_codebase
from app.models.schemas import ChatRequest, ChatResponse
from app.services.codebase import CodebaseService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, codebase: CodebaseService = Depends(get_codebase)):
    answer, sources = await codebase.answer(request.message)
    return ChatResponse(
        message=answer,
        sources=sources,
        conversation_id=request.conversation_id or "new",
        model_used=codebase.chat_model.model_name,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest, codebase: CodebaseService = Depends(get_codebase)):
    answer_stream = await codebase.answer_stream(request.message)
    return StreamingResponse(answer_stream, media_type="text/plain")
