"""
LLM Service
===========
Service for interacting with Large Language Models (OpenAI/Anthropic).
Handles prompt building and response generation.
"""

from typing import List, Optional, AsyncIterator
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.config import settings
from app.models.schemas import CodeChunk, ChatMessage


class LLMService:
    """
    Service for generating responses using LLMs.
    """

    def __init__(self):
        """Initialize the LLM client."""
        self.provider = settings.llm_provider
        self.model = settings.model_name
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature

        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def build_prompt(
        self,
        question: str,
        context_chunks: List[CodeChunk],
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> List[Dict[str, str]]:
        """
        Build the prompt for the LLM with retrieved code context.

        Args:
            question: User's question
            context_chunks: Retrieved code chunks
            conversation_history: Previous messages (optional)

        Returns:
            List of message dicts in ChatML format
        """
        # System message
        system_prompt = """You are CodeMate AI, an expert code assistant.

Your role:
- Answer questions based ONLY on the provided code context
- Provide specific line references when mentioning code
- Include code snippets in your answers
- If the answer is not in the context, clearly state that
- Be concise but thorough

Format your responses using markdown:
- Use ```language for code blocks
- Use `inline code` for short snippets
- Use **bold** for important points
"""

        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(
                f"""Source {i}:
File: {chunk.file_name}
Lines: {chunk.line_start}-{chunk.line_end}
Language: {chunk.language.value}

```{chunk.language.value}
{chunk.content}
```
"""
            )

        context = "\n\n".join(context_parts)

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })

        # Add current question with context
        user_message = f"""Code Context:
{context}

Question: {question}

Please answer based on the code context provided above."""

        messages.append({"role": "user", "content": user_message})

        return messages

    async def generate_response(
        self,
        question: str,
        context_chunks: List[CodeChunk],
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """
        Generate a response using the LLM.

        Args:
            question: User's question
            context_chunks: Retrieved code chunks
            conversation_history: Previous messages (optional)

        Returns:
            Generated response
        """
        messages = self.build_prompt(question, context_chunks, conversation_history)

        if self.provider == "openai":
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            # Anthropic has different message format
            system_msg = messages[0]["content"]
            user_messages = [{"role": m["role"], "content": m["content"]}
                           for m in messages[1:]]

            response = await self.client.messages.create(
                model=self.model,
                system=system_msg,
                messages=user_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.content[0].text

    async def generate_response_stream(
        self,
        question: str,
        context_chunks: List[CodeChunk],
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response (real-time token-by-token).

        Args:
            question: User's question
            context_chunks: Retrieved code chunks
            conversation_history: Previous messages (optional)

        Yields:
            Response chunks as they're generated
        """
        messages = self.build_prompt(question, context_chunks, conversation_history)

        if self.provider == "openai":
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        elif self.provider == "anthropic":
            system_msg = messages[0]["content"]
            user_messages = [{"role": m["role"], "content": m["content"]}
                           for m in messages[1:]]

            async with self.client.messages.stream(
                model=self.model,
                system=system_msg,
                messages=user_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            ) as stream:
                async for text in stream.text_stream:
                    yield text


async def test_llm_service():
    """Test the LLM service."""
    from app.models.schemas import CodeLanguage

    print("🧪 Testing LLM Service...")

    service = LLMService()

    # Mock code chunks
    chunks = [
        CodeChunk(
            id="1",
            file_name="auth.py",
            content="def login(username, password):\n    return authenticate(username, password)",
            language=CodeLanguage.PYTHON,
            line_start=10,
            line_end=12,
            metadata={}
        )
    ]

    # Test generation
    print("\n1. Testing response generation:")
    question = "How does the login function work?"
    response = await service.generate_response(question, chunks)
    print(f"   Q: {question}")
    print(f"   A: {response[:200]}...")

    print("\n✅ Tests completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_llm_service())
