import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import ChatSession, ChatMessage

router = APIRouter()

@router.post("/new")
def create_new_session(db: Session = Depends(get_db)):
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    new_session = ChatSession(session_id=session_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.session_id, "created_at": new_session.created_at}

@router.get("/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "risk_level": session.risk_level,
        "messages": [
            {
                "message_id": m.message_id,
                "sender": m.sender,
                "message_type": m.message_type,
                "text_content": m.text_content,
                "media_url": m.media_url,
                "created_at": m.created_at
            }
            for m in messages
        ]
    }
