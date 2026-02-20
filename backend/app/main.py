"""
CodeMate AI - FastAPI Backend
==============================
Main application entry point.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional

from app.core.config import settings, validate_settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    SearchRequest,
    SearchResponse,
    UploadResponse,
    HealthResponse,
    ErrorResponse,
    MessageRole
)
from app.services.embeddings import EmbeddingsService
from app.services.vector_store import VectorStore
from app.services.parser import CodeParser
from app.services.llm import LLMService


# ========== Application Lifecycle ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Runs on startup and shutdown.
    """
    # Startup
    print("🚀 Starting CodeMate AI...")
    validate_settings()

    # Initialize services
    app.state.embeddings = EmbeddingsService()
    app.state.vector_store = VectorStore()
    app.state.parser = CodeParser(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    app.state.llm = LLMService()

    print("✅ All services initialized")

    yield

    # Shutdown
    print("👋 Shutting down CodeMate AI...")


# ========== FastAPI App ==========

app = FastAPI(
    title="CodeMate AI",
    description="RAG-Powered Code Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== API Endpoints ==========

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    stats = await app.state.vector_store.get_stats()

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        llm_provider=settings.llm_provider,
        vector_db=settings.vector_db,
        total_chunks=stats["total_chunks"]
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_code(
    file: UploadFile = File(...)
):
    """
    Upload a code file and process it.

    Process:
    1. Parse file into chunks
    2. Generate embeddings
    3. Store in vector database
    """
    try:
        # Read file content
        content = await file.read()
        content = content.decode("utf-8")

        # Parse into chunks
        chunks = app.state.parser.parse_file(
            file_name=file.filename,
            content=content,
            strategy="functions"  # or "fixed_size"
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="No code chunks extracted")

        # Generate embeddings
        embeddings = await app.state.embeddings.create_embeddings_batch(
            [chunk.content for chunk in chunks]
        )

        # Store in vector database
        await app.state.vector_store.add_chunks(chunks, embeddings)

        return UploadResponse(
            success=True,
            file_name=file.filename,
            chunks_created=len(chunks),
            language=chunks[0].language,
            message=f"Successfully processed {len(chunks)} chunks"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - ask questions about your code.

    Process:
    1. Create embedding for question
    2. Search for relevant code chunks
    3. Generate response using LLM
    """
    try:
        # Create query embedding
        query_embedding = await app.state.embeddings.create_embedding(request.message)

        # Search for relevant code
        search_results = await app.state.vector_store.search(
            query_embedding=query_embedding,
            top_k=settings.top_k
        )

        if not search_results:
            return ChatResponse(
                message="I couldn't find any relevant code for your question. Please upload some code first.",
                sources=[],
                conversation_id=request.conversation_id or "new",
                model_used=settings.model_name,
                tokens_used=0
            )

        # Extract chunks
        context_chunks = [result.chunk for result in search_results]

        # Generate response
        response_text = await app.state.llm.generate_response(
            question=request.message,
            context_chunks=context_chunks
        )

        return ChatResponse(
            message=response_text,
            sources=context_chunks,
            conversation_id=request.conversation_id or "new",
            model_used=settings.model_name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint - returns responses in real-time.
    """
    try:
        # Create query embedding
        query_embedding = await app.state.embeddings.create_embedding(request.message)

        # Search for relevant code
        search_results = await app.state.vector_store.search(
            query_embedding=query_embedding,
            top_k=settings.top_k
        )

        if not search_results:
            async def no_results_stream():
                yield "I couldn't find any relevant code for your question."

            return StreamingResponse(
                no_results_stream(),
                media_type="text/plain"
            )

        # Extract chunks
        context_chunks = [result.chunk for result in search_results]

        # Generate streaming response
        async def generate():
            async for chunk in app.state.llm.generate_response_stream(
                question=request.message,
                context_chunks=context_chunks
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_code(request: SearchRequest):
    """
    Search for code semantically (by meaning, not just keywords).
    """
    try:
        # Create query embedding
        query_embedding = await app.state.embeddings.create_embedding(request.query)

        # Search
        results = await app.state.vector_store.search(
            query_embedding=query_embedding,
            top_k=request.top_k or settings.top_k
        )

        # Filter by min score
        if request.min_score:
            results = [r for r in results if r.score >= request.min_score]

        return SearchResponse(
            results=results,
            total=len(results),
            query=request.query
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/files/{file_name}")
async def delete_file(file_name: str):
    """Delete all chunks from a specific file."""
    try:
        deleted_count = await app.state.vector_store.delete_by_file(file_name)

        return {
            "success": True,
            "file_name": file_name,
            "chunks_deleted": deleted_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get statistics about the vector database."""
    try:
        stats = await app.state.vector_store.get_stats()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Run Server ==========

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
