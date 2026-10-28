from fastapi import APIRouter, Depends

from app.dependencies import get_codebase
from app.models.schemas import SearchRequest, SearchResponse
from app.services.codebase import CodebaseService

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, codebase: CodebaseService = Depends(get_codebase)):
    results = await codebase.search(request.query, top_k=request.top_k)
    if request.min_score:
        results = [result for result in results if result.score >= request.min_score]
    return SearchResponse(results=results, total=len(results), query=request.query)
