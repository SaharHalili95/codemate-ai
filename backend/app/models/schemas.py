"""
Data Models (Pydantic Schemas)
===============================
כל המודלים לבדיקת נתונים (validation) באפליקציה
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


# ========== Enums ==========

class CodeLanguage(str, Enum):
    """שפות תכנות נתמכות"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    UNKNOWN = "unknown"


class MessageRole(str, Enum):
    """תפקידים בצ'אט"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ========== Request Models ==========

class UploadFileRequest(BaseModel):
    """
    Request להעלאת קובץ קוד
    """
    file_name: str = Field(..., description="שם הקובץ")
    content: str = Field(..., description="תוכן הקובץ")
    language: Optional[CodeLanguage] = Field(None, description="שפת תכנות (אוטומטי אם לא מצוין)")

    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "main.py",
                "content": "def hello():\n    print('Hello World')",
                "language": "python"
            }
        }


class ChatMessage(BaseModel):
    """
    הודעה בצ'אט
    """
    role: MessageRole = Field(..., description="תפקיד השולח")
    content: str = Field(..., description="תוכן ההודעה")
    timestamp: Optional[str] = Field(None, description="זמן שליחה")


class ChatRequest(BaseModel):
    """
    Request לשאלה בצ'אט
    """
    message: str = Field(..., min_length=1, max_length=5000, description="השאלה")
    conversation_id: Optional[str] = Field(None, description="מזהה שיחה (לשמירת היסטוריה)")
    include_history: bool = Field(True, description="האם לכלול היסטוריית שיחה")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "How does the login function work?",
                "conversation_id": "conv_123",
                "include_history": True
            }
        }


class SearchRequest(BaseModel):
    """
    Request לחיפוש קוד
    """
    query: str = Field(..., min_length=1, description="שאילתת החיפוש")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="כמות תוצאות")
    min_score: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="ציון מינימום")
    filters: Optional[Dict[str, Any]] = Field(None, description="פילטרים נוספים")


# ========== Response Models ==========

class CodeChunk(BaseModel):
    """
    קטע קוד
    """
    id: str = Field(..., description="מזהה ייחודי")
    file_name: str = Field(..., description="שם הקובץ")
    content: str = Field(..., description="תוכן הקטע")
    language: CodeLanguage = Field(..., description="שפת תכנות")
    line_start: int = Field(..., ge=1, description="שורה התחלתית")
    line_end: int = Field(..., ge=1, description="שורה סופית")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="מטא-דאטה נוסף")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chunk_123",
                "file_name": "auth.py",
                "content": "def login(username, password):\n    ...",
                "language": "python",
                "line_start": 10,
                "line_end": 25,
                "metadata": {"function_name": "login"}
            }
        }


class SearchResult(BaseModel):
    """
    תוצאת חיפוש
    """
    chunk: CodeChunk = Field(..., description="קטע הקוד")
    score: float = Field(..., ge=0.0, le=1.0, description="ציון רלוונטיות")
    distance: Optional[float] = Field(None, description="מרחק וקטורי")


class SearchResponse(BaseModel):
    """
    Response לחיפוש
    """
    results: List[SearchResult] = Field(..., description="תוצאות החיפוש")
    total: int = Field(..., ge=0, description="סך כל התוצאות")
    query: str = Field(..., description="השאילתה המקורית")


class ChatResponse(BaseModel):
    """
    Response לצ'אט
    """
    message: str = Field(..., description="תשובת המערכת")
    sources: List[CodeChunk] = Field(default_factory=list, description="מקורות קוד שנמצאו")
    conversation_id: str = Field(..., description="מזהה שיחה")
    model_used: str = Field(..., description="המודל ששימש")
    tokens_used: Optional[int] = Field(None, description="כמות tokens ששימשו")


class UploadResponse(BaseModel):
    """
    Response להעלאת קובץ
    """
    success: bool = Field(..., description="האם ההעלאה הצליחה")
    file_name: str = Field(..., description="שם הקובץ")
    chunks_created: int = Field(..., ge=0, description="כמות chunks שנוצרו")
    language: CodeLanguage = Field(..., description="שפה שזוהתה")
    message: str = Field(..., description="הודעת סטטוס")


class HealthResponse(BaseModel):
    """
    Response לבדיקת בריאות המערכת
    """
    status: str = Field(..., description="סטטוס המערכת")
    version: str = Field(..., description="גרסת API")
    llm_provider: str = Field(..., description="ספק LLM")
    vector_db: str = Field(..., description="מסד נתונים וקטורי")
    total_chunks: int = Field(..., ge=0, description="סך כל ה-chunks במערכת")


# ========== Error Models ==========

class ErrorResponse(BaseModel):
    """
    Response לשגיאה
    """
    error: str = Field(..., description="סוג השגיאה")
    message: str = Field(..., description="תיאור השגיאה")
    detail: Optional[Dict[str, Any]] = Field(None, description="פרטים נוספים")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input format",
                "detail": {"field": "message", "issue": "too short"}
            }
        }
