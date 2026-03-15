"""
Configuration Management
========================
קובץ זה מנהל את כל ההגדרות של האפליקציה.
משתמש ב-pydantic-settings לקריאה מקובץ .env
"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """
    הגדרות האפליקציה

    כל ההגדרות נקראות מקובץ .env
    אם לא מוגדר ערך, נלקח ה-default
    """

    # ========== LLM Configuration ==========
    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    model_name: str = "gpt-4-turbo-preview"
    max_tokens: int = 2000
    temperature: float = 0.1

    # ========== Vector Database ==========
    vector_db: Literal["chromadb", "pinecone"] = "chromadb"
    chroma_path: str = "./data/chroma"

    # ========== Embeddings ==========
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    # ========== Chunking ==========
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_chunks_per_file: int = 100

    # ========== Retrieval ==========
    top_k: int = 5
    similarity_threshold: float = 0.7

    # ========== Server ==========
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # ========== Demo Mode ==========
    demo_mode: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# יצירת instance גלובלי של ההגדרות
settings = Settings()


# ========== Validation ==========
def validate_settings():
    """
    בודק שכל ההגדרות הנדרשות מוגדרות
    """
    if settings.demo_mode:
        print("⚡ Running in DEMO MODE — no API key required")
        return

    if settings.llm_provider == "openai" and not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when using OpenAI")

    if settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic")

    if settings.chunk_size <= 0:
        raise ValueError("CHUNK_SIZE must be positive")

    if settings.chunk_overlap >= settings.chunk_size:
        raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")

    print("✅ Configuration validated successfully")


if __name__ == "__main__":
    # בדיקה של ההגדרות
    print("Current configuration:")
    print(f"LLM Provider: {settings.llm_provider}")
    print(f"Model: {settings.model_name}")
    print(f"Vector DB: {settings.vector_db}")
    print(f"Chunk Size: {settings.chunk_size}")

    validate_settings()
