import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings, validate_settings
from app.routes import api_router
from app.services.codebase import CodebaseService
from app.services.embeddings import DemoEmbedder, OpenAIEmbedder
from app.services.llm import create_chat_model
from app.services.parser import CodeParser
from app.services.vector_store import VectorStore

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_settings()
    app.state.codebase = CodebaseService(
        parser=CodeParser(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap),
        embedder=DemoEmbedder() if settings.demo_mode else OpenAIEmbedder(),
        store=VectorStore(),
        chat_model=create_chat_model(),
        top_k=settings.top_k,
    )
    logger.info("CodeMate AI started (demo mode: %s)", settings.demo_mode)
    yield


app = FastAPI(
    title="CodeMate AI",
    description="RAG-Powered Code Assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://codemate-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.reload)
