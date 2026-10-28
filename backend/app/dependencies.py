from fastapi import Request

from app.services.codebase import CodebaseService


def get_codebase(request: Request) -> CodebaseService:
    return request.app.state.codebase
