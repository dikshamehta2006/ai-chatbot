from fastapi import APIRouter
from backend.app.api.endpoints import chat, session, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(session.router, prefix="/session", tags=["Session"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
