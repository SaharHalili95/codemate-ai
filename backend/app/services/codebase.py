from typing import AsyncIterator

from app.models.schemas import CodeChunk, SearchResult
from app.services.embeddings import Embedder
from app.services.llm import ChatModel
from app.services.parser import CodeParser
from app.services.vector_store import VectorStore


class CodebaseService:
    """Indexes uploaded code and answers questions about it (the RAG pipeline)."""

    def __init__(
        self,
        parser: CodeParser,
        embedder: Embedder,
        store: VectorStore,
        chat_model: ChatModel,
        top_k: int,
    ):
        self.parser = parser
        self.embedder = embedder
        self.store = store
        self.chat_model = chat_model
        self.top_k = top_k

    async def index_file(self, file_name: str, content: str) -> list[CodeChunk]:
        chunks = self.parser.parse_file(file_name, content, strategy="functions")
        if chunks:
            embeddings = await self.embedder.embed_batch([chunk.content for chunk in chunks])
            await self.store.add_chunks(chunks, embeddings)
        return chunks

    async def search(self, query: str, top_k: int | None = None) -> list[SearchResult]:
        query_embedding = await self.embedder.embed(query)
        return await self.store.search(query_embedding, top_k=top_k or self.top_k)

    async def answer(self, question: str) -> tuple[str, list[CodeChunk]]:
        sources = await self._find_sources(question)
        return await self.chat_model.answer(question, sources), sources

    async def answer_stream(self, question: str) -> AsyncIterator[str]:
        sources = await self._find_sources(question)
        return self.chat_model.answer_stream(question, sources)

    async def delete_file(self, file_name: str) -> int:
        return await self.store.delete_by_file(file_name)

    async def stats(self) -> dict:
        return await self.store.get_stats()

    async def _find_sources(self, question: str) -> list[CodeChunk]:
        return [result.chunk for result in await self.search(question)]
