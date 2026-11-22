from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    dominant_mood = Column(String(50), nullable=True)
    risk_level = Column(String(20), default="NORMAL")  # NORMAL, ELEVATED, CRISIS

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    safety_logs = relationship("SafetyAuditLog", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    message_id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # USER, ASSISTANT, SYSTEM
    message_type = Column(String(20), default="TEXT")  # TEXT, IMAGE, AUDIO, MULTIMODAL
    text_content = Column(Text, nullable=True)
    media_url = Column(String(255), nullable=True)
    media_mime_type = Column(String(50), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    guardrail_flagged = Column(Boolean, default=False)
    rag_context_used = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class SafetyAuditLog(Base):
    __tablename__ = "safety_audit_logs"

    log_id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    trigger_type = Column(String(50), nullable=False)  # SELF_HARM, VIOLENCE, PII_LEAK, PROMPT_INJECTION
    input_snippet = Column(Text, nullable=True)
    action_taken = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="safety_logs")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    doc_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
