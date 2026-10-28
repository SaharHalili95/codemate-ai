from app.models.schemas import CodeChunk


def demo_chat_response(question: str, context_chunks: list[CodeChunk]) -> str:
    q = question.lower()

    file_names = list({c.file_name for c in context_chunks})
    files_str = ", ".join(f"`{f}`" for f in file_names) if file_names else "the uploaded files"

    if any(w in q for w in ["how", "explain", "what does", "describe"]):
        template = (
            f"Based on the code in {files_str}, here's how it works:\n\n"
            f"The implementation follows a clear pattern:\n\n"
        )
    elif any(w in q for w in ["bug", "error", "fix", "issue", "problem"]):
        template = (
            f"Looking at {files_str}, I can identify a potential issue:\n\n"
        )
    elif any(w in q for w in ["test", "testing"]):
        template = (
            f"To test the code in {files_str}, you could:\n\n"
        )
    elif any(w in q for w in ["improve", "optimize", "refactor", "better"]):
        template = (
            f"Here are suggestions to improve {files_str}:\n\n"
        )
    else:
        template = (
            f"Analyzing the code in {files_str}:\n\n"
        )

    if context_chunks:
        chunk = context_chunks[0]
        lines = chunk.content.strip().split("\n")
        snippet = "\n".join(lines[:min(8, len(lines))])
        body = (
            f"The relevant section is in `{chunk.file_name}` "
            f"(lines {chunk.line_start}–{chunk.line_end}):\n\n"
            f"```{chunk.language.value}\n{snippet}\n```\n\n"
            f"**Key observations:**\n"
            f"- The code is written in **{chunk.language.value}** and spans {chunk.line_end - chunk.line_start + 1} lines\n"
            f"- It follows standard conventions for this language\n"
            f"- The logic is straightforward and readable\n\n"
            f"> 💡 *Demo mode — responses are illustrative. Connect an API key for full AI-powered analysis.*"
        )
    else:
        body = (
            "No code has been uploaded yet. Please upload a file first using the upload button, "
            "then ask questions about your codebase.\n\n"
            "> 💡 *Demo mode — upload any code file to see the RAG pipeline in action.*"
        )

    return template + body
