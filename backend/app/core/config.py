import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
(UPLOADS_DIR / "images").mkdir(exist_ok=True)
(UPLOADS_DIR / "audio").mkdir(exist_ok=True)
(UPLOADS_DIR / "tts").mkdir(exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Multimodal Emotional Support Chatbot"
    API_V1_PREFIX: str = "/api/v1"
    
    # Gemini LLM Config
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_FALLBACK_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    
    # Database Settings (MySQL default, SQLite seamless fallback for development)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "emotional_support_db"
    
    # Optional direct DATABASE_URL override
    DATABASE_URL: str = ""
    
    # Storage Paths
    BASE_DIR: Path = BASE_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    KNOWLEDGE_DOCS_DIR: Path = BASE_DIR / "knowledge_docs"
    
    # Guardrails
    ENABLE_GUARDRAILS: bool = True
    MAX_FILE_SIZE_MB: int = 15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Return standard MySQL URL with pymysql driver
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

settings = Settings()
