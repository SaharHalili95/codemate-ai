import hashlib
import random
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from app.core.config import settings


class Embedder(ABC):
    """Turns text into vectors for semantic search."""

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...

    async def embed(self, text: str) -> list[float]:
        return (await self.embed_batch([text]))[0]


class OpenAIEmbedder(Embedder):
    BATCH_SIZE = 100

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for start in range(0, len(texts), self.BATCH_SIZE):
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts[start:start + self.BATCH_SIZE],
                encoding_format="float",
            )
            embeddings.extend(item.embedding for item in response.data)
        return embeddings


class DemoEmbedder(Embedder):
    """Deterministic pseudo-embeddings, so search works without an API key."""

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    @staticmethod
    def _embed_one(text: str) -> list[float]:
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2 ** 32)
        rng = random.Random(seed)
        return [rng.uniform(-1.0, 1.0) for _ in range(settings.embedding_dim)]
