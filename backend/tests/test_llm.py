import asyncio

from app.models.schemas import CodeChunk, CodeLanguage
from app.services.llm import NO_SOURCES_MESSAGE, LLMChatModel, build_user_message

CHUNK = CodeChunk(
    id="1",
    file_name="auth.py",
    content="def login(): ...",
    language=CodeLanguage.PYTHON,
    line_start=10,
    line_end=12,
)


class RecordingChatModel(LLMChatModel):
    provider = "fake"

    def __init__(self):
        super().__init__()
        self.prompts = []

    async def _complete(self, user_message):
        self.prompts.append(user_message)
        return "answer"

    async def _stream(self, user_message):
        self.prompts.append(user_message)
        for word in ("streamed", "answer"):
            yield word


async def collect(stream):
    return [text async for text in stream]


def test_answer_without_sources_skips_the_api():
    model = RecordingChatModel()

    assert asyncio.run(model.answer("question", [])) == NO_SOURCES_MESSAGE
    assert asyncio.run(collect(model.answer_stream("question", []))) == [NO_SOURCES_MESSAGE]
    assert model.prompts == []


def test_answer_and_stream_send_the_same_prompt():
    model = RecordingChatModel()

    asyncio.run(model.answer("How does login work?", [CHUNK]))
    asyncio.run(collect(model.answer_stream("How does login work?", [CHUNK])))

    assert model.prompts[0] == model.prompts[1]


def test_prompt_cites_file_and_lines():
    prompt = build_user_message("How does login work?", [CHUNK])

    assert "File: auth.py" in prompt
    assert "Lines: 10-12" in prompt
    assert prompt.endswith("Please answer based on the code context provided above.")
