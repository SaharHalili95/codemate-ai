"""
Demo Mode Service
=================
Returns realistic mock responses without any API key.
Used when DEMO_MODE=true is set in environment.
"""

import random
import hashlib
from typing import List
from app.models.schemas import CodeChunk, CodeLanguage


def demo_embedding(text: str) -> List[float]:
    """
    Generate a deterministic pseudo-embedding from text.
    Uses a seeded random so the same text always gets the same vector,
    which makes ChromaDB similarity search work meaningfully in demo mode.
    """
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2 ** 32)
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(1536)]


def demo_chat_response(question: str, context_chunks: List[CodeChunk]) -> str:
    """
    Generate a realistic-looking demo response based on the question and code context.
    """
    q = question.lower()

    # Build a context summary from the actual chunks
    file_names = list({c.file_name for c in context_chunks})
    files_str = ", ".join(f"`{f}`" for f in file_names) if file_names else "the uploaded files"

    if any(w in q for w in ["how", "explain", "what does", "describe"]):
        template = (
            f"Based on the code in {files_str}, here's how it works:\n\n"
            f"The implementation follows a clear pattern:\n\n"
        )
    elif any(w in q for w in ["bug", "error", "fix", "issue", "problem"]):
        template = (
            f"Looking at {files_str}, I can identify a potential issue:\n\n"
        )
    elif any(w in q for w in ["test", "testing"]):
        template = (
            f"To test the code in {files_str}, you could:\n\n"
        )
    elif any(w in q for w in ["improve", "optimize", "refactor", "better"]):
        template = (
            f"Here are suggestions to improve {files_str}:\n\n"
        )
    else:
        template = (
            f"Analyzing the code in {files_str}:\n\n"
        )

    # Add chunk-specific content
    if context_chunks:
        chunk = context_chunks[0]
        lines = chunk.content.strip().split("\n")
        snippet = "\n".join(lines[:min(8, len(lines))])
        body = (
            f"The relevant section is in `{chunk.file_name}` "
            f"(lines {chunk.line_start}–{chunk.line_end}):\n\n"
            f"```{chunk.language.value}\n{snippet}\n```\n\n"
            f"**Key observations:**\n"
            f"- The code is written in **{chunk.language.value}** and spans {chunk.line_end - chunk.line_start + 1} lines\n"
            f"- It follows standard conventions for this language\n"
            f"- The logic is straightforward and readable\n\n"
            f"> 💡 *Demo mode — responses are illustrative. Connect an API key for full AI-powered analysis.*"
        )
    else:
        body = (
            "No code has been uploaded yet. Please upload a file first using the upload button, "
            "then ask questions about your codebase.\n\n"
            "> 💡 *Demo mode — upload any code file to see the RAG pipeline in action.*"
        )

    return template + body


def demo_upload_response(file_name: str, chunks: List[CodeChunk]) -> dict:
    """Return a realistic upload summary for demo mode."""
    return {
        "success": True,
        "file_name": file_name,
        "chunks_created": len(chunks),
        "language": chunks[0].language if chunks else CodeLanguage.UNKNOWN,
        "message": f"✅ Demo mode: processed {len(chunks)} chunks from {file_name}",
    }
