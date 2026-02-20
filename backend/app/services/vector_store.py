"""
Vector Store Service
====================
שירות לניהול Vector Database (ChromaDB)

מה זה Vector Database?
-----------------------
מסד נתונים מיוחד לשמירה וחיפוש של vectors (embeddings).
במקום לחפש לפי שוויון (SQL: WHERE name = 'John'),
מחפשים לפי דמיון (Vector DB: find similar to X).

הפעולות:
---------
1. INSERT - הוספת vectors חדשים
2. SEARCH - מציאת vectors הכי דומים (KNN)
3. UPDATE - עדכון vectors
4. DELETE - מחיקת vectors
"""

from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
import uuid

from app.core.config import settings
from app.models.schemas import CodeChunk, SearchResult


class VectorStore:
    """
    שירות לניהול Vector Database עם ChromaDB

    ChromaDB - מסד נתונים וקטורי local, קל להתקנה, חינמי!
    """

    def __init__(self, collection_name: str = "code_chunks"):
        """
        אתחול Vector Store

        Args:
            collection_name: שם האוסף (כמו "table" ב-SQL)
        """
        self.collection_name = collection_name

        # אתחול ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # יצירת או טעינת collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Code chunks with embeddings"}
        )

        print(f"✅ VectorStore initialized: {collection_name}")
        print(f"   Total items: {self.collection.count()}")

    async def add_chunks(
        self,
        chunks: List[CodeChunk],
        embeddings: List[List[float]]
    ) -> int:
        """
        מוסיף code chunks למסד הנתונים

        Args:
            chunks: רשימת code chunks
            embeddings: רשימת vectors (באותו אורך!)

        Returns:
            int: כמות chunks שנוספו

        Example:
            >>> chunks = [CodeChunk(...), CodeChunk(...)]
            >>> embeddings = [[0.1, 0.2, ...], [0.3, 0.4, ...]]
            >>> count = await store.add_chunks(chunks, embeddings)
            >>> count
            2
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        if not chunks:
            return 0

        # הכנת הנתונים ל-ChromaDB
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [
            {
                "file_name": chunk.file_name,
                "language": chunk.language.value,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                **chunk.metadata
            }
            for chunk in chunks
        ]

        # הוספה למסד הנתונים
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        print(f"✅ Added {len(chunks)} chunks to vector store")
        return len(chunks)

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        מחפש code chunks דומים לquery

        איך זה עובד?
        1. מקבל query embedding
        2. מחפש את top_k vectors הכי קרובים
        3. מחזיר את הקוד המקורי + ציון

        Args:
            query_embedding: vector של השאלה
            top_k: כמה תוצאות להחזיר
            filters: פילטרים (למשל: {"language": "python"})

        Returns:
            List[SearchResult]: תוצאות החיפוש

        Example:
            >>> query_vec = await embeddings.create_embedding("login function")
            >>> results = await store.search(query_vec, top_k=3)
            >>> for result in results:
            ...     print(f"Score: {result.score:.2f} - {result.chunk.file_name}")
            Score: 0.89 - auth.py
            Score: 0.76 - user.py
            Score: 0.68 - admin.py
        """
        # חיפוש ב-ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters  # פילטרים אופציונליים
        )

        # המרה לSearchResult objects
        search_results = []

        if not results["ids"] or not results["ids"][0]:
            return search_results

        for i in range(len(results["ids"][0])):
            chunk_id = results["ids"][0][i]
            document = results["documents"][0][i]
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i] if "distances" in results else None

            # יצירת CodeChunk
            chunk = CodeChunk(
                id=chunk_id,
                file_name=metadata.get("file_name", "unknown"),
                content=document,
                language=metadata.get("language", "unknown"),
                line_start=metadata.get("line_start", 1),
                line_end=metadata.get("line_end", 1),
                metadata={k: v for k, v in metadata.items()
                         if k not in ["file_name", "language", "line_start", "line_end"]}
            )

            # חישוב score (ChromaDB מחזיר distance, נהפוך ל-similarity)
            # Distance: 0 = זהים, ככל שגדל יותר → פחות דומים
            # Score: 1 = זהים, 0 = לא דומים
            score = 1.0 / (1.0 + distance) if distance is not None else 1.0

            search_results.append(
                SearchResult(
                    chunk=chunk,
                    score=score,
                    distance=distance
                )
            )

        # סינון לפי threshold
        search_results = [
            r for r in search_results
            if r.score >= settings.similarity_threshold
        ]

        # מיון לפי score (גבוה לנמוך)
        search_results.sort(key=lambda x: x.score, reverse=True)

        return search_results

    async def delete_by_file(self, file_name: str) -> int:
        """
        מחק את כל ה-chunks של קובץ מסוים

        Args:
            file_name: שם הקובץ למחיקה

        Returns:
            int: כמות chunks שנמחקו

        Example:
            >>> deleted = await store.delete_by_file("old_code.py")
            >>> deleted
            15
        """
        # מציאת כל ה-chunks של הקובץ
        results = self.collection.get(
            where={"file_name": file_name}
        )

        if not results["ids"]:
            return 0

        # מחיקה
        self.collection.delete(ids=results["ids"])

        print(f"🗑️  Deleted {len(results['ids'])} chunks from {file_name}")
        return len(results["ids"])

    async def get_chunk_by_id(self, chunk_id: str) -> Optional[CodeChunk]:
        """
        מחזיר chunk לפי ID

        Args:
            chunk_id: מזהה ה-chunk

        Returns:
            Optional[CodeChunk]: ה-chunk או None
        """
        results = self.collection.get(ids=[chunk_id])

        if not results["ids"]:
            return None

        metadata = results["metadatas"][0]
        return CodeChunk(
            id=chunk_id,
            file_name=metadata.get("file_name", "unknown"),
            content=results["documents"][0],
            language=metadata.get("language", "unknown"),
            line_start=metadata.get("line_start", 1),
            line_end=metadata.get("line_end", 1),
            metadata={k: v for k, v in metadata.items()
                     if k not in ["file_name", "language", "line_start", "line_end"]}
        )

    async def get_stats(self) -> Dict[str, Any]:
        """
        מחזיר סטטיסטיקות על מסד הנתונים

        Returns:
            dict: סטטיסטיקות

        Example:
            >>> stats = await store.get_stats()
            >>> stats
            {
                'total_chunks': 1523,
                'languages': {'python': 850, 'javascript': 673},
                'files': 42
            }
        """
        all_data = self.collection.get()

        if not all_data["metadatas"]:
            return {
                "total_chunks": 0,
                "languages": {},
                "files": 0
            }

        # ספירת שפות
        languages = {}
        files = set()

        for metadata in all_data["metadatas"]:
            lang = metadata.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1
            files.add(metadata.get("file_name", "unknown"))

        return {
            "total_chunks": len(all_data["ids"]),
            "languages": languages,
            "files": len(files),
            "collection_name": self.collection_name
        }

    async def reset(self):
        """
        מוחק את כל הנתונים במסד (זהירות!)

        Example:
            >>> await store.reset()
            ⚠️  Vector store reset complete
        """
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Code chunks with embeddings"}
        )
        print(f"⚠️  Vector store '{self.collection_name}' reset complete")


# ========== Helper Functions ==========

async def test_vector_store():
    """
    פונקציית test לבדיקת השירות
    הרץ: python -m app.services.vector_store
    """
    print("🧪 Testing Vector Store...")

    from app.services.embeddings import EmbeddingsService
    from app.models.schemas import CodeLanguage

    store = VectorStore(collection_name="test_collection")
    embeddings_service = EmbeddingsService()

    # נקה מבדיקות קודמות
    await store.reset()

    # Test 1: Add chunks
    print("\n1️⃣ Adding chunks:")
    chunks = [
        CodeChunk(
            id=str(uuid.uuid4()),
            file_name="auth.py",
            content="def login(username, password):\n    return authenticate(username, password)",
            language=CodeLanguage.PYTHON,
            line_start=10,
            line_end=12,
            metadata={"function_name": "login"}
        ),
        CodeChunk(
            id=str(uuid.uuid4()),
            file_name="user.py",
            content="def create_user(email, name):\n    user = User(email=email, name=name)\n    return user.save()",
            language=CodeLanguage.PYTHON,
            line_start=20,
            line_end=23,
            metadata={"function_name": "create_user"}
        )
    ]

    embeddings = await embeddings_service.create_embeddings_batch(
        [chunk.content for chunk in chunks]
    )
    count = await store.add_chunks(chunks, embeddings)
    print(f"   Added {count} chunks")

    # Test 2: Search
    print("\n2️⃣ Searching:")
    query = "authentication function"
    query_embedding = await embeddings_service.create_embedding(query)
    results = await store.search(query_embedding, top_k=2)
    print(f"   Query: '{query}'")
    print(f"   Found {len(results)} results:")
    for result in results:
        print(f"   - Score: {result.score:.3f} | {result.chunk.file_name}:{result.chunk.line_start}")

    # Test 3: Stats
    print("\n3️⃣ Stats:")
    stats = await store.get_stats()
    print(f"   {stats}")

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_vector_store())
