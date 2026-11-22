import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.db.database import init_db
from backend.app.rag.vector_store import vector_store
from backend.app.api.routes import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("emotional_chatbot.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Database...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    logger.info("Initializing RAG Knowledge Store...")
    try:
        vector_store.initialize()
    except Exception as e:
        logger.error(f"RAG initialization failed: {e}")

    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Secure Multimodal Emotional Support Chatbot API with RAG & Guardrails",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for audio/image uploads & generated TTS
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
