import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

logger = logging.getLogger("emotional_chatbot.database")
Base = declarative_base()

def get_engine():
    mysql_url = settings.get_database_url()
    try:
        # First attempt connecting to MySQL
        engine = create_engine(
            mysql_url,
            pool_recycle=3600,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3}
        )
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected to MySQL database at {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
        return engine
    except Exception as e:
        logger.warning(
            f"MySQL connection failed ({e}). "
            "Falling back to local SQLite database ('emotional_support.db') to ensure zero-downtime operation."
        )
        fallback_url = "sqlite:///./emotional_support.db"
        return create_engine(fallback_url, connect_args={"check_same_thread": False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables in the configured database."""
    from backend.app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database tables initialized on {engine.dialect.name}.")

# Auto-initialize tables on module import to ensure tables exist immediately
try:
    init_db()
except Exception as _e:
    logger.warning(f"Initial table auto-creation notice: {_e}")
