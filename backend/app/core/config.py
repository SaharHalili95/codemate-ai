from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    model_name: str = "gpt-4-turbo-preview"
    max_tokens: int = 2000
    temperature: float = 0.1

    vector_db: Literal["chromadb"] = "chromadb"
    chroma_path: str = "./data/chroma"

    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    chunk_size: int = 1000
    chunk_overlap: int = 200

    top_k: int = 5
    similarity_threshold: float = 0.7

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    demo_mode: bool = False


settings = Settings()


def validate_settings():
    if settings.chunk_size <= 0:
        raise ValueError("CHUNK_SIZE must be positive")
    if settings.chunk_overlap >= settings.chunk_size:
        raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
    if settings.demo_mode:
        return
    # Embeddings always come from OpenAI, whichever provider answers the questions.
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for embeddings")
    if settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic")
