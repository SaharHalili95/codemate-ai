"""
Code Parser Service
===================
Service for parsing and chunking code files.

Strategies:
- Fixed size chunking
- Function-based chunking (using tree-sitter)
- Semantic chunking
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import re
import uuid

from app.models.schemas import CodeChunk, CodeLanguage


class CodeParser:
    """
    Parser for extracting meaningful chunks from code files.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the parser.

        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def detect_language(self, file_name: str, content: Optional[str] = None) -> CodeLanguage:
        """
        Detect programming language from file extension or content.

        Args:
            file_name: Name of the file
            content: File content (optional, for better detection)

        Returns:
            CodeLanguage: Detected language
        """
        ext = Path(file_name).suffix.lower()

        extension_map = {
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

        return extension_map.get(ext, CodeLanguage.UNKNOWN)

    def chunk_by_fixed_size(
        self,
        file_name: str,
        content: str,
        language: Optional[CodeLanguage] = None
    ) -> List[CodeChunk]:
        """
        Split code into fixed-size chunks with overlap.

        Args:
            file_name: Name of the source file
            content: Code content
            language: Programming language (auto-detected if None)

        Returns:
            List of CodeChunk objects
        """
        if not content:
            return []

        if language is None:
            language = self.detect_language(file_name)

        chunks = []
        lines = content.split("\n")
        current_chunk = []
        current_size = 0
        current_line = 1

        for i, line in enumerate(lines, 1):
            current_chunk.append(line)
            current_size += len(line) + 1  # +1 for newline

            # Check if we've reached chunk size
            if current_size >= self.chunk_size:
                chunk_content = "\n".join(current_chunk)
                chunks.append(
                    CodeChunk(
                        id=str(uuid.uuid4()),
                        file_name=file_name,
                        content=chunk_content,
                        language=language,
                        line_start=current_line,
                        line_end=i,
                        metadata={"chunk_method": "fixed_size"}
                    )
                )

                # Calculate overlap
                overlap_lines = []
                overlap_size = 0
                for line in reversed(current_chunk):
                    if overlap_size >= self.chunk_overlap:
                        break
                    overlap_lines.insert(0, line)
                    overlap_size += len(line) + 1

                current_chunk = overlap_lines
                current_size = overlap_size
                current_line = i - len(overlap_lines) + 1

        # Add remaining content
        if current_chunk:
            chunk_content = "\n".join(current_chunk)
            chunks.append(
                CodeChunk(
                    id=str(uuid.uuid4()),
                    file_name=file_name,
                    content=chunk_content,
                    language=language,
                    line_start=current_line,
                    line_end=len(lines),
                    metadata={"chunk_method": "fixed_size"}
                )
            )

        return chunks

    def chunk_by_functions(
        self,
        file_name: str,
        content: str,
        language: Optional[CodeLanguage] = None
    ) -> List[CodeChunk]:
        """
        Split code by functions/methods (simplified version).

        This is a basic regex-based implementation.
        For production, use tree-sitter for AST parsing.

        Args:
            file_name: Name of the source file
            content: Code content
            language: Programming language (auto-detected if None)

        Returns:
            List of CodeChunk objects
        """
        if not content:
            return []

        if language is None:
            language = self.detect_language(file_name)

        chunks = []
        lines = content.split("\n")

        # Language-specific function patterns
        patterns = {
            CodeLanguage.PYTHON: r"^\s*def\s+\w+\s*\(",
            CodeLanguage.JAVASCRIPT: r"^\s*(function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\()",
            CodeLanguage.TYPESCRIPT: r"^\s*(function\s+\w+|const\s+\w+\s*:\s*\(|export\s+function)",
            CodeLanguage.JAVA: r"^\s*(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(",
        }

        pattern = patterns.get(language)
        if not pattern:
            # Fallback to fixed size
            return self.chunk_by_fixed_size(file_name, content, language)

        current_function = []
        function_start = 1

        for i, line in enumerate(lines, 1):
            if re.match(pattern, line) and current_function:
                # Save previous function
                func_content = "\n".join(current_function)
                if func_content.strip():
                    chunks.append(
                        CodeChunk(
                            id=str(uuid.uuid4()),
                            file_name=file_name,
                            content=func_content,
                            language=language,
                            line_start=function_start,
                            line_end=i - 1,
                            metadata={"chunk_method": "function"}
                        )
                    )

                current_function = [line]
                function_start = i
            else:
                current_function.append(line)

        # Add last function
        if current_function:
            func_content = "\n".join(current_function)
            if func_content.strip():
                chunks.append(
                    CodeChunk(
                        id=str(uuid.uuid4()),
                        file_name=file_name,
                        content=func_content,
                        language=language,
                        line_start=function_start,
                        line_end=len(lines),
                        metadata={"chunk_method": "function"}
                    )
                )

        return chunks if chunks else self.chunk_by_fixed_size(file_name, content, language)

    def parse_file(
        self,
        file_name: str,
        content: str,
        strategy: str = "fixed_size"
    ) -> List[CodeChunk]:
        """
        Parse a code file into chunks.

        Args:
            file_name: Name of the file
            content: File content
            strategy: Chunking strategy ("fixed_size" or "functions")

        Returns:
            List of CodeChunk objects
        """
        if strategy == "functions":
            return self.chunk_by_functions(file_name, content)
        else:
            return self.chunk_by_fixed_size(file_name, content)


def test_parser():
    """Test the parser with sample code."""
    parser = CodeParser(chunk_size=100, chunk_overlap=20)

    # Test Python code
    python_code = """
def login(username, password):
    if not username or not password:
        return False
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return True
    return False

def logout(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_active = False
        user.save()
    return True
"""

    print("Testing Parser...")
    print("\n1. Fixed size chunking:")
    chunks = parser.parse_file("auth.py", python_code, strategy="fixed_size")
    for i, chunk in enumerate(chunks, 1):
        print(f"   Chunk {i}: lines {chunk.line_start}-{chunk.line_end}, {len(chunk.content)} chars")

    print("\n2. Function-based chunking:")
    chunks = parser.parse_file("auth.py", python_code, strategy="functions")
    for i, chunk in enumerate(chunks, 1):
        print(f"   Chunk {i}: lines {chunk.line_start}-{chunk.line_end}")
        print(f"   Preview: {chunk.content[:50]}...")

    print("\n✅ Tests completed!")


if __name__ == "__main__":
    test_parser()
