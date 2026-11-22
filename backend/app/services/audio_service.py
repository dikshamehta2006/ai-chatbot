import os
import uuid
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Optional
from backend.app.core.config import settings

logger = logging.getLogger("emotional_chatbot.audio")

def generate_speech_response(text: str, session_id: str) -> Optional[str]:
    """
    Converts assistant response text to spoken audio.
    Supports macOS native offline synthesis (say + afconvert) and gTTS fallback.
    Returns the relative web path to the audio file.
    """
    if not text or not text.strip():
        return None

    try:
        clean_text = clean_text_for_speech(text)
        if not clean_text:
            return None

        # Truncate overly long text for audio
        if len(clean_text) > 600:
            clean_text = clean_text[:600] + "... Take a slow breath, I am here with you."

        filename_base = f"{session_id}_{uuid.uuid4().hex[:8]}"

        # Strategy 1: macOS native offline TTS ('say' + 'afconvert' -> .wav)
        if shutil.which("say") and shutil.which("afconvert"):
            try:
                aiff_path = settings.UPLOADS_DIR / "tts" / f"{filename_base}.aiff"
                wav_path = settings.UPLOADS_DIR / "tts" / f"{filename_base}.wav"
                
                # Use calming Samantha or default voice
                subprocess.run(
                    ["say", "-o", str(aiff_path), clean_text],
                    check=True,
                    timeout=10,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Convert AIFF to standard PCM WAV for HTML5 browser audio playback
                subprocess.run(
                    ["afconvert", "-f", "WAVE", "-d", "LEI16", str(aiff_path), str(wav_path)],
                    check=True,
                    timeout=10,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Clean up intermediate aiff file
                if aiff_path.exists():
                    aiff_path.unlink()

                logger.info(f"Generated offline native audio at {wav_path}")
                return f"/uploads/tts/{filename_base}.wav"
            except Exception as say_err:
                logger.debug(f"macOS offline TTS attempt: {say_err}")

        # Strategy 2: gTTS (Google Text-To-Speech) fallback
        try:
            from gtts import gTTS
            mp3_path = settings.UPLOADS_DIR / "tts" / f"{filename_base}.mp3"
            tts = gTTS(text=clean_text, lang='en', slow=False)
            tts.save(str(mp3_path))
            logger.info(f"Generated gTTS audio at {mp3_path}")
            return f"/uploads/tts/{filename_base}.mp3"
        except Exception as gtts_err:
            logger.debug(f"gTTS fallback failed: {gtts_err}")

        return None
    except Exception as e:
        logger.error(f"Speech synthesis error: {e}")
        return None

def clean_text_for_speech(text: str) -> str:
    import re
    # Remove markdown headers, bold, italics, links, emojis, and list markers
    t = re.sub(r"#+\s*", "", text)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"[-*•]\s+", "", t)
    t = re.sub(r"[^\w\s.,?!'\"]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()
