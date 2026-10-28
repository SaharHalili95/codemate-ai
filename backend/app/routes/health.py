from fastapi import APIRouter, Depends

from app.core.config import settings
from app.dependencies import get_codebase
from app.models.schemas import HealthResponse
from app.services.codebase import CodebaseService

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health(codebase: CodebaseService = Depends(get_codebase)):
    stats = await codebase.stats()
    return HealthResponse(
        status="healthy (demo)" if settings.demo_mode else "healthy",
        version="1.0.0",
        llm_provider=codebase.chat_model.provider,
        vector_db=settings.vector_db,
        total_chunks=stats["total_chunks"],
    )


@router.get("/stats")
async def stats(codebase: CodebaseService = Depends(get_codebase)):
    return await codebase.stats()
