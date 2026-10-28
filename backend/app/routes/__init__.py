from fastapi import APIRouter

from app.routes import chat, files, health, search

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(files.router)
api_router.include_router(chat.router)
api_router.include_router(search.router)
