from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.database import get_db, engine
from backend.app.core.config import settings
from backend.app.rag.vector_store import vector_store

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Check DB
    db_status = "unhealthy"
    db_type = "unknown"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
        db_type = engine.dialect.name
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check Gemini API Key
    gemini_status = "configured" if settings.GEMINI_API_KEY else "api_key_missing"

    # Check Vector Store
    vector_store.initialize()
    rag_chunks = len(vector_store.chunks)

    return {
        "status": "healthy",
        "database": {
            "status": db_status,
            "dialect": db_type,
            "host": settings.MYSQL_HOST if db_type == "mysql" else "local_sqlite"
        },
        "gemini": {
            "status": gemini_status,
            "model": settings.GEMINI_MODEL
        },
        "rag": {
            "indexed_chunks": rag_chunks,
            "status": "ready" if rag_chunks > 0 else "empty"
        }
    }
