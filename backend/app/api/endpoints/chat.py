import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.guardrails import evaluate_guardrails
from backend.app.core.prompts import CRISIS_FALLBACK_RESPONSE
from backend.app.db.database import get_db
from backend.app.db.models import ChatSession, ChatMessage, SafetyAuditLog
from backend.app.rag.retriever import get_rag_context
from backend.app.services.gemini_service import gemini_service
from backend.app.services.audio_service import generate_speech_response

logger = logging.getLogger("emotional_chatbot.chat")
router = APIRouter()

@router.post("/message")
async def send_chat_message(
    session_id: str = Form(...),
    message: Optional[str] = Form(""),
    generate_audio: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # 1. Validate session
    session_record = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session_record:
        session_record = ChatSession(session_id=session_id)
        db.add(session_record)
        db.commit()

    saved_image_path = None
    saved_audio_path = None
    media_url = None
    media_mime = None
    message_type = "TEXT"

    # 2. Handle image upload if present
    if image and image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            img_filename = f"{session_id}_{uuid.uuid4().hex[:8]}{ext}"
            target_path = settings.UPLOADS_DIR / "images" / img_filename
            with open(target_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            saved_image_path = str(target_path)
            media_url = f"/uploads/images/{img_filename}"
            media_mime = image.content_type
            message_type = "IMAGE" if not audio else "MULTIMODAL"

    # 3. Handle audio upload if present
    if audio and audio.filename:
        ext = Path(audio.filename).suffix.lower()
        if ext in [".wav", ".mp3", ".ogg", ".m4a"]:
            aud_filename = f"{session_id}_{uuid.uuid4().hex[:8]}{ext}"
            target_path = settings.UPLOADS_DIR / "audio" / aud_filename
            with open(target_path, "wb") as buffer:
                shutil.copyfileobj(audio.file, buffer)
            saved_audio_path = str(target_path)
            media_url = f"/uploads/audio/{aud_filename}"
            media_mime = audio.content_type
            message_type = "AUDIO" if message_type == "TEXT" else "MULTIMODAL"

    user_text = (message or "").strip()
    if not user_text and not saved_image_path and not saved_audio_path:
        raise HTTPException(status_code=400, detail="Cannot send an empty message without media.")

    # 4. Guardrails check on user text
    guardrail_res = evaluate_guardrails(user_text)
    
    # 5. Save user message to database
    user_msg_db = ChatMessage(
        session_id=session_id,
        sender="USER",
        message_type=message_type,
        text_content=guardrail_res.sanitized_text if user_text else "[Shared Media]",
        media_url=media_url,
        media_mime_type=media_mime,
        guardrail_flagged=not guardrail_res.is_safe
    )
    db.add(user_msg_db)
    db.commit()

    # 6. Critical Crisis Protocol
    if guardrail_res.is_crisis:
        # Log to safety audit log
        audit_log = SafetyAuditLog(
            session_id=session_id,
            trigger_type="SELF_HARM",
            input_snippet=user_text[:200],
            action_taken="DISPATCH_EMERGENCY_HOTLINES"
        )
        db.add(audit_log)
        session_record.risk_level = "CRISIS"
        db.commit()

        # Generate audio response for crisis if requested
        response_audio_url = None
        if generate_audio:
            crisis_speech_snippet = (
                "I hear how much pain you are carrying right now, and I care deeply about your safety. "
                "You do not have to carry this alone. Please reach out to the 988 Suicide and Crisis Lifeline, "
                "or call your local emergency services right now. Your life matters."
            )
            response_audio_url = generate_speech_response(crisis_speech_snippet, session_id)

        # Save assistant crisis message
        bot_msg_db = ChatMessage(
            session_id=session_id,
            sender="ASSISTANT",
            message_type="TEXT" if not response_audio_url else "MULTIMODAL",
            text_content=CRISIS_FALLBACK_RESPONSE,
            media_url=response_audio_url,
            media_mime_type="audio/mpeg" if response_audio_url else None,
            guardrail_flagged=True
        )
        db.add(bot_msg_db)
        db.commit()

        return {
            "session_id": session_id,
            "response": CRISIS_FALLBACK_RESPONSE,
            "audio_url": response_audio_url,
            "is_crisis": True,
            "guardrail_flagged": True,
            "rag_sources": []
        }

    # 7. RAG Knowledge Retrieval
    rag_context, rag_sources = get_rag_context(user_text, top_k=2)

    # 8. Gemini Generation
    assistant_text = gemini_service.generate_multimodal_response(
        prompt=guardrail_res.sanitized_text or "Please reflect on the media I shared.",
        image_path=saved_image_path,
        audio_path=saved_audio_path,
        rag_context=rag_context
    )

    # 9. Voice Synthesis (TTS)
    response_audio_url = None
    if generate_audio and assistant_text:
        response_audio_url = generate_speech_response(assistant_text, session_id)

    # 10. Persist Assistant Message
    bot_msg_db = ChatMessage(
        session_id=session_id,
        sender="ASSISTANT",
        message_type="TEXT" if not response_audio_url else "MULTIMODAL",
        text_content=assistant_text,
        media_url=response_audio_url,
        media_mime_type="audio/mpeg" if response_audio_url else None,
        rag_context_used=rag_sources if rag_sources else None,
        guardrail_flagged=not guardrail_res.is_safe
    )
    db.add(bot_msg_db)
    db.commit()

    return {
        "session_id": session_id,
        "response": assistant_text,
        "audio_url": response_audio_url,
        "is_crisis": False,
        "guardrail_flagged": not guardrail_res.is_safe,
        "guardrail_reasons": guardrail_res.reasons,
        "rag_sources": [s["title"] for s in rag_sources]
    }
