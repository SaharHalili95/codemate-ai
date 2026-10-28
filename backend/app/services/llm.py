import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.core.config import settings
from app.models.schemas import CodeChunk
from app.services.demo import demo_chat_response

SYSTEM_PROMPT = """You are CodeMate AI, an expert code assistant.

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

NO_SOURCES_MESSAGE = (
    "I couldn't find any relevant code for your question. Please upload some code first."
)


class ChatModel(ABC):
    """Answers a question using the code chunks retrieved for it."""

    provider: str
    model_name: str

    @abstractmethod
    async def answer(self, question: str, sources: list[CodeChunk]) -> str: ...

    @abstractmethod
    def answer_stream(self, question: str, sources: list[CodeChunk]) -> AsyncIterator[str]: ...


class LLMChatModel(ChatModel):
    """Builds the prompt once; each provider only implements how to call its API."""

    def __init__(self):
        self.model_name = settings.model_name
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature

    async def answer(self, question: str, sources: list[CodeChunk]) -> str:
        if not sources:
            return NO_SOURCES_MESSAGE
        return await self._complete(build_user_message(question, sources))

    async def answer_stream(self, question: str, sources: list[CodeChunk]) -> AsyncIterator[str]:
        if not sources:
            yield NO_SOURCES_MESSAGE
            return
        async for text in self._stream(build_user_message(question, sources)):
            yield text

    @abstractmethod
    async def _complete(self, user_message: str) -> str: ...

    @abstractmethod
    def _stream(self, user_message: str) -> AsyncIterator[str]: ...


class OpenAIChatModel(LLMChatModel):
    provider = "openai"

    def __init__(self):
        super().__init__()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def _complete(self, user_message: str) -> str:
        response = await self.client.chat.completions.create(**self._request(user_message))
        return response.choices[0].message.content

    async def _stream(self, user_message: str) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(**self._request(user_message), stream=True)
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _request(self, user_message: str) -> dict:
        return {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


class AnthropicChatModel(LLMChatModel):
    provider = "anthropic"

    def __init__(self):
        super().__init__()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def _complete(self, user_message: str) -> str:
        response = await self.client.messages.create(**self._request(user_message))
        return response.content[0].text

    async def _stream(self, user_message: str) -> AsyncIterator[str]:
        async with self.client.messages.stream(**self._request(user_message)) as stream:
            async for text in stream.text_stream:
                yield text

    def _request(self, user_message: str) -> dict:
        return {
            "model": self.model_name,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_message}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


class DemoChatModel(ChatModel):
    provider = "demo"
    model_name = "demo"
    WORD_DELAY_SECONDS = 0.03

    async def answer(self, question: str, sources: list[CodeChunk]) -> str:
        return demo_chat_response(question, sources)

    async def answer_stream(self, question: str, sources: list[CodeChunk]) -> AsyncIterator[str]:
        for word in demo_chat_response(question, sources).split(" "):
            yield word + " "
            await asyncio.sleep(self.WORD_DELAY_SECONDS)


def create_chat_model() -> ChatModel:
    if settings.demo_mode:
        return DemoChatModel()
    if settings.llm_provider == "anthropic":
        return AnthropicChatModel()
    return OpenAIChatModel()


def build_user_message(question: str, sources: list[CodeChunk]) -> str:
    context = "\n\n".join(
        f"Source {number}:\n"
        f"File: {chunk.file_name}\n"
        f"Lines: {chunk.line_start}-{chunk.line_end}\n"
        f"Language: {chunk.language.value}\n\n"
        f"```{chunk.language.value}\n{chunk.content}\n```"
        for number, chunk in enumerate(sources, 1)
    )
    return (
        f"Code Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Please answer based on the code context provided above."
    )
