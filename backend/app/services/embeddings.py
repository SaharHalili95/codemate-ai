"""
Embeddings Service
==================
שירות ליצירת embeddings (vectors) מטקסט

מה זה embeddings?
-----------------
המרה של טקסט למערך מספרים שמייצג את המשמעות שלו.
טקסטים עם משמעות דומה יקבלו vectors דומים.

דוגמה:
"login function" → [0.23, -0.45, 0.67, ..., 0.12]
"authentication" → [0.25, -0.43, 0.69, ..., 0.14]  ← דומה!
"pizza recipe" → [-0.82, 0.91, -0.34, ..., 0.56]  ← שונה!
"""

from typing import List, Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import asyncio

from app.core.config import settings


class EmbeddingsService:
    """
    שירות ליצירת embeddings

    תומך ב:
    - OpenAI (text-embedding-3-small, text-embedding-3-large)
    - Anthropic (voyage embeddings)
    """

    def __init__(self):
        """אתחול השירות"""
        self.provider = settings.llm_provider
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dim

        # אתחול הלקוח המתאים
        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def create_embedding(self, text: str) -> List[float]:
        """
        יוצר embedding עבור טקסט בודד

        Args:
            text: הטקסט להמרה

        Returns:
            List[float]: vector של מספרים (embedding)

        Example:
            >>> service = EmbeddingsService()
            >>> vector = await service.create_embedding("def login():")
            >>> len(vector)
            1536
            >>> type(vector[0])
            <class 'float'>
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if self.provider == "openai":
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"  # מחזיר מספרים רגילים
            )
            return response.data[0].embedding

        elif self.provider == "anthropic":
            # Anthropic משתמש ב-Voyage AI לembeddings
            # TODO: implement when available
            raise NotImplementedError("Anthropic embeddings not yet implemented")

    async def create_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        יוצר embeddings עבור רשימת טקסטים (batch processing)

        למה batch? מהיר יותר ומשתמש בפחות API calls!

        Args:
            texts: רשימת טקסטים
            batch_size: כמה טקסטים בקריאה אחת

        Returns:
            List[List[float]]: רשימת vectors

        Example:
            >>> texts = ["def login():", "def logout():", "def signup():"]
            >>> vectors = await service.create_embeddings_batch(texts)
            >>> len(vectors)
            3
            >>> len(vectors[0])
            1536
        """
        if not texts:
            return []

        # סינון טקסטים ריקים
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return []

        all_embeddings = []

        # חלוקה ל-batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            if self.provider == "openai":
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float"
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

            elif self.provider == "anthropic":
                raise NotImplementedError("Anthropic embeddings not yet implemented")

        return all_embeddings

    async def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        מחשב דמיון בין שני vectors (cosine similarity)

        Cosine Similarity:
        - 1.0 = זהים לחלוטין
        - 0.0 = לא קשורים
        - -1.0 = הפוכים

        Args:
            embedding1: vector ראשון
            embedding2: vector שני

        Returns:
            float: ציון דמיון (0-1)

        Example:
            >>> v1 = await service.create_embedding("login function")
            >>> v2 = await service.create_embedding("authentication")
            >>> similarity = await service.compute_similarity(v1, v2)
            >>> similarity
            0.85  # דומים מאוד!
        """
        import math

        # בדיקת אורך
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have the same dimension")

        # חישוב dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))

        # חישוב magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))

        # חישוב cosine similarity
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        similarity = dot_product / (magnitude1 * magnitude2)
        return max(0.0, min(1.0, similarity))  # normalize to 0-1

    def get_embedding_stats(self, embedding: List[float]) -> dict:
        """
        מחזיר סטטיסטיקות על embedding (לdebug)

        Args:
            embedding: vector

        Returns:
            dict: סטטיסטיקות

        Example:
            >>> stats = service.get_embedding_stats(vector)
            >>> stats
            {
                'dimension': 1536,
                'mean': 0.023,
                'std': 0.156,
                'min': -0.89,
                'max': 0.91
            }
        """
        import statistics

        return {
            "dimension": len(embedding),
            "mean": statistics.mean(embedding),
            "std": statistics.stdev(embedding) if len(embedding) > 1 else 0,
            "min": min(embedding),
            "max": max(embedding),
        }


# ========== Helper Functions ==========

async def test_embeddings_service():
    """
    פונקציית test לבדיקת השירות
    הרץ: python -m app.services.embeddings
    """
    print("🧪 Testing Embeddings Service...")

    service = EmbeddingsService()

    # Test 1: Single embedding
    print("\n1️⃣ Testing single embedding:")
    text = "def login(username, password):"
    embedding = await service.create_embedding(text)
    print(f"   Text: {text}")
    print(f"   Dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")

    # Test 2: Batch embeddings
    print("\n2️⃣ Testing batch embeddings:")
    texts = [
        "def login():",
        "def authenticate():",
        "def pizza():"
    ]
    embeddings = await service.create_embeddings_batch(texts)
    print(f"   Created {len(embeddings)} embeddings")

    # Test 3: Similarity
    print("\n3️⃣ Testing similarity:")
    sim1 = await service.compute_similarity(embeddings[0], embeddings[1])
    sim2 = await service.compute_similarity(embeddings[0], embeddings[2])
    print(f"   login <-> authenticate: {sim1:.4f}")
    print(f"   login <-> pizza: {sim2:.4f}")
    print(f"   ✅ {'login' and 'authenticate' are more similar!" if sim1 > sim2 else '❌ Something wrong!'}")

    # Test 4: Stats
    print("\n4️⃣ Embedding stats:")
    stats = service.get_embedding_stats(embedding)
    print(f"   {stats}")

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # הרצת tests
    asyncio.run(test_embeddings_service())
