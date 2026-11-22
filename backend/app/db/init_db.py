import sys
import logging
from sqlalchemy import create_engine, text
from backend.app.core.config import settings
from backend.app.db.database import Base, engine
from backend.app.db import models  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("emotional_chatbot.init_db")

def setup_mysql_database():
    """Attempts to connect to MySQL server and ensure the target database exists."""
    server_url = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}"
    try:
        logger.info(f"Connecting to MySQL server at {settings.MYSQL_HOST}:{settings.MYSQL_PORT}...")
        server_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
        with server_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
        logger.info(f"Database '{settings.MYSQL_DATABASE}' verified / created.")
    except Exception as e:
        logger.warning(f"Could not connect to MySQL server: {e}")
        logger.info("Proceeding with default engine initialization...")

def init_tables():
    logger.info("Creating all database tables (sessions, messages, audit logs, knowledge docs)...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully!")

if __name__ == "__main__":
    setup_mysql_database()
    init_tables()
