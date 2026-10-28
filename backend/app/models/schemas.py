from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CodeLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    UNKNOWN = "unknown"


class ChatRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"message": "How does the login function work?", "conversation_id": "conv_123"}}
    )

    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int | None = Field(5, ge=1, le=20)
    min_score: float | None = Field(0.7, ge=0.0, le=1.0)


class CodeChunk(BaseModel):
    id: str
    file_name: str
    content: str
    language: CodeLanguage
    line_start: int = Field(..., ge=1)
    line_end: int = Field(..., ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    chunk: CodeChunk
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance, 1 = identical")
    distance: float | None = Field(None, description="Raw vector distance from ChromaDB")


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int = Field(..., ge=0)
    query: str


class ChatResponse(BaseModel):
    message: str
    sources: list[CodeChunk] = Field(default_factory=list)
    conversation_id: str
    model_used: str


class UploadResponse(BaseModel):
    success: bool
    file_name: str
    chunks_created: int = Field(..., ge=0)
    language: CodeLanguage
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_provider: str
    vector_db: str
    total_chunks: int = Field(..., ge=0)
