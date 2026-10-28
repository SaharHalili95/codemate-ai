from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.dependencies import get_codebase
from app.models.schemas import UploadResponse
from app.services.codebase import CodebaseService

router = APIRouter(tags=["files"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    codebase: CodebaseService = Depends(get_codebase),
):
    try:
        content = (await file.read()).decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 text")

    chunks = await codebase.index_file(file.filename, content)
    if not chunks:
        raise HTTPException(status_code=400, detail="No code chunks extracted")

    return UploadResponse(
        success=True,
        file_name=file.filename,
        chunks_created=len(chunks),
        language=chunks[0].language,
        message=f"Successfully processed {len(chunks)} chunks",
    )


@router.delete("/files/{file_name}")
async def delete_file(file_name: str, codebase: CodebaseService = Depends(get_codebase)):
    deleted_count = await codebase.delete_file(file_name)
    return {"success": True, "file_name": file_name, "chunks_deleted": deleted_count}
