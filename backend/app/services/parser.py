import re
import uuid
from pathlib import Path

from app.models.schemas import CodeChunk, CodeLanguage

EXTENSION_LANGUAGES = {
    ".py": CodeLanguage.PYTHON,
    ".js": CodeLanguage.JAVASCRIPT,
    ".jsx": CodeLanguage.JAVASCRIPT,
    ".ts": CodeLanguage.TYPESCRIPT,
    ".tsx": CodeLanguage.TYPESCRIPT,
    ".java": CodeLanguage.JAVA,
    ".cpp": CodeLanguage.CPP,
    ".cc": CodeLanguage.CPP,
    ".cxx": CodeLanguage.CPP,
    ".hpp": CodeLanguage.CPP,
    ".go": CodeLanguage.GO,
    ".rs": CodeLanguage.RUST,
}

FUNCTION_START_PATTERNS = {
    CodeLanguage.PYTHON: r"^\s*def\s+\w+\s*\(",
    CodeLanguage.JAVASCRIPT: r"^\s*(function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\()",
    CodeLanguage.TYPESCRIPT: r"^\s*(function\s+\w+|const\s+\w+\s*:\s*\(|export\s+function)",
    CodeLanguage.JAVA: r"^\s*(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(",
}


class CodeParser:
    """Splits a source file into chunks small enough to embed."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def parse_file(self, file_name: str, content: str, strategy: str = "fixed_size") -> list[CodeChunk]:
        if not content:
            return []
        language = detect_language(file_name)
        if strategy == "functions":
            return self.chunk_by_functions(file_name, content, language)
        return self.chunk_by_fixed_size(file_name, content, language)

    def chunk_by_fixed_size(self, file_name: str, content: str, language: CodeLanguage) -> list[CodeChunk]:
        """Cuts on line boundaries once a chunk reaches chunk_size characters.

        Each new chunk starts with the last chunk_overlap characters' worth of lines
        from the previous one, so code that spans a cut stays searchable.
        """
        chunks = []
        lines = content.split("\n")
        current_lines: list[str] = []
        current_size = 0
        start_line = 1

        for line_number, line in enumerate(lines, 1):
            current_lines.append(line)
            current_size += len(line) + 1

            if current_size >= self.chunk_size:
                chunks.append(_make_chunk(file_name, current_lines, language, start_line, line_number, "fixed_size"))
                current_lines = self._overlap_tail(current_lines)
                current_size = sum(len(overlap_line) + 1 for overlap_line in current_lines)
                start_line = line_number - len(current_lines) + 1

        if current_lines:
            chunks.append(_make_chunk(file_name, current_lines, language, start_line, len(lines), "fixed_size"))

        return chunks

    def chunk_by_functions(self, file_name: str, content: str, language: CodeLanguage) -> list[CodeChunk]:
        pattern = FUNCTION_START_PATTERNS.get(language)
        if not pattern:
            return self.chunk_by_fixed_size(file_name, content, language)

        chunks = []
        lines = content.split("\n")
        current_lines: list[str] = []
        start_line = 1

        for line_number, line in enumerate(lines, 1):
            if re.match(pattern, line) and current_lines:
                if "\n".join(current_lines).strip():
                    chunks.append(_make_chunk(file_name, current_lines, language, start_line, line_number - 1, "function"))
                current_lines = []
                start_line = line_number
            current_lines.append(line)

        if "\n".join(current_lines).strip():
            chunks.append(_make_chunk(file_name, current_lines, language, start_line, len(lines), "function"))

        return chunks or self.chunk_by_fixed_size(file_name, content, language)

    def _overlap_tail(self, lines: list[str]) -> list[str]:
        tail: list[str] = []
        size = 0
        for line in reversed(lines):
            if size >= self.chunk_overlap:
                break
            tail.insert(0, line)
            size += len(line) + 1
        return tail


def detect_language(file_name: str) -> CodeLanguage:
    return EXTENSION_LANGUAGES.get(Path(file_name).suffix.lower(), CodeLanguage.UNKNOWN)


def _make_chunk(
    file_name: str,
    lines: list[str],
    language: CodeLanguage,
    line_start: int,
    line_end: int,
    method: str,
) -> CodeChunk:
    return CodeChunk(
        id=str(uuid.uuid4()),
        file_name=file_name,
        content="\n".join(lines),
        language=language,
        line_start=line_start,
        line_end=line_end,
        metadata={"chunk_method": method},
    )
