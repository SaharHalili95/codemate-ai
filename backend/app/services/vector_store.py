import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from app.models.schemas import CodeChunk, SearchResult

logger = logging.getLogger(__name__)

CHUNK_FIELDS = ("file_name", "language", "line_start", "line_end")


class VectorStore:
    """Stores code chunks with their embeddings in ChromaDB and finds the closest ones."""

    def __init__(self, collection_name: str = "code_chunks"):
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)

    async def add_chunks(self, chunks: list[CodeChunk], embeddings: list[list[float]]) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        if not chunks:
            return 0

        self.collection.add(
            ids=[chunk.id for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.content for chunk in chunks],
            metadatas=[
                {
                    "file_name": chunk.file_name,
                    "language": chunk.language.value,
                    "line_start": chunk.line_start,
                    "line_end": chunk.line_end,
                    **chunk.metadata,
                }
                for chunk in chunks
            ],
        )
        logger.info("Added %d chunks to the vector store", len(chunks))
        return len(chunks)

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters,
        )

        search_results = []
        for chunk_id, document, metadata, distance in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # Chroma returns a distance (0 = identical); map it to a 0-1 similarity score.
            score = 1.0 / (1.0 + distance)
            if score >= settings.similarity_threshold:
                search_results.append(
                    SearchResult(chunk=_to_chunk(chunk_id, document, metadata), score=score, distance=distance)
                )

        return sorted(search_results, key=lambda result: result.score, reverse=True)

    async def delete_by_file(self, file_name: str) -> int:
        ids = self.collection.get(where={"file_name": file_name})["ids"]
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    async def get_stats(self) -> dict[str, Any]:
        metadatas = self.collection.get(include=["metadatas"])["metadatas"] or []

        languages: dict[str, int] = {}
        files = set()
        for metadata in metadatas:
            language = metadata.get("language", "unknown")
            languages[language] = languages.get(language, 0) + 1
            files.add(metadata.get("file_name", "unknown"))

        return {
            "total_chunks": len(metadatas),
            "languages": languages,
            "files": len(files),
            "collection_name": self.collection_name,
        }


def _to_chunk(chunk_id: str, document: str, metadata: dict[str, Any]) -> CodeChunk:
    return CodeChunk(
        id=chunk_id,
        file_name=metadata.get("file_name", "unknown"),
        content=document,
        language=metadata.get("language", "unknown"),
        line_start=metadata.get("line_start", 1),
        line_end=metadata.get("line_end", 1),
        metadata={key: value for key, value in metadata.items() if key not in CHUNK_FIELDS},
    )
