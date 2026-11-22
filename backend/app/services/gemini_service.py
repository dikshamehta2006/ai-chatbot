import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from PIL import Image

from backend.app.core.config import settings
from backend.app.core.prompts import MASTER_SYSTEM_PROMPT
from backend.app.core.guardrails import verify_output_safety

logger = logging.getLogger("emotional_chatbot.gemini")

class GeminiService:
    def __init__(self):
        self._is_configured = False
        self._setup_client()

    def _setup_client(self):
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self._is_configured = True
                logger.info("Google Gemini SDK configured successfully.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini SDK: {e}")
                self._is_configured = False
        else:
            logger.warning("No GEMINI_API_KEY found. Running in mock/fallback mode until key is provided.")
            self._is_configured = False

    def generate_multimodal_response(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        rag_context: str = "",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Sends multimodal inputs to Google Gemini and returns an empathetic, grounded response.
        """
        # Re-check key in case it was updated in .env or os.environ
        if not self._is_configured:
            self._setup_client()

        if not self._is_configured:
            return self._generate_fallback_response(prompt, rag_context)

        try:
            import google.generativeai as genai

            # Model safety settings
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
            ]

            # Try requested model, with fallback to 1.5-flash
            model_name = settings.GEMINI_MODEL
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=MASTER_SYSTEM_PROMPT,
                    safety_settings=safety_settings
                )
            except Exception:
                model = genai.GenerativeModel(
                    model_name=settings.GEMINI_FALLBACK_MODEL,
                    system_instruction=MASTER_SYSTEM_PROMPT,
                    safety_settings=safety_settings
                )

            # Build multimodal contents list
            contents = []

            # Add RAG context if available
            if rag_context:
                contents.append(f"{rag_context}\n\nUser Message: {prompt}")
            else:
                contents.append(prompt)

            # Attach image if provided
            if image_path and Path(image_path).exists():
                try:
                    img = Image.open(image_path)
                    contents.append(img)
                    logger.info(f"Attached image from {image_path}")
                except Exception as img_err:
                    logger.error(f"Failed to load image for Gemini: {img_err}")

            # Attach audio if provided
            if audio_path and Path(audio_path).exists():
                try:
                    audio_file = genai.upload_file(path=audio_path)
                    contents.append(audio_file)
                    logger.info(f"Uploaded audio to Gemini: {audio_file.name}")
                except Exception as aud_err:
                    logger.error(f"Failed to upload audio to Gemini: {aud_err}")

            # Generate content
            response = model.generate_content(contents)
            raw_text = response.text if response and response.text else "I am here with you. Could you share a little more about what you're experiencing?"
            
            # Post-generation safety check
            safe_text = verify_output_safety(raw_text)
            return safe_text

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return self._generate_fallback_response(prompt, rag_context)

    def _generate_fallback_response(self, prompt: str, rag_context: str) -> str:
        """
        Provides a compassionate fallback response incorporating retrieved RAG exercises
        when Gemini API key is missing or offline.
        """
        intro = "I hear you, and I want to acknowledge what you're feeling right now. "
        
        if rag_context and "Box Breathing" in rag_context:
            coping = (
                "Let's take a gentle pause together. A proven somatic technique is **Box Breathing**:\n\n"
                "1. **Inhale** slowly through your nose for 4 counts.\n"
                "2. **Hold** gently for 4 counts.\n"
                "3. **Exhale** completely through your mouth for 4 counts.\n"
                "4. **Rest** with empty lungs for 4 counts.\n\n"
                "How does your body feel as you take that breath?"
            )
        elif rag_context and "5-4-3-2-1" in rag_context:
            coping = (
                "When your mind feels crowded, the **5-4-3-2-1 Grounding exercise** can help anchor you:\n\n"
                "- Name **5 things you see** around you right now.\n"
                "- Name **4 things you can physically touch**.\n"
                "- Name **3 sounds you can hear**.\n"
                "- Name **2 scents you can smell**.\n"
                "- Name **1 taste you can sense**.\n\n"
                "Take all the time you need. I'm right here with you."
            )
        elif rag_context and "TIPP" in rag_context:
            coping = (
                "When emotions feel overwhelming, the DBT **TIPP skill** can quickly reset your nervous system:\n\n"
                "- **Temperature**: Splash cool water on your face or hold something cool.\n"
                "- **Paced Breathing**: Inhale for 4 seconds, exhale slowly for 7 seconds.\n"
                "- **Paired Relaxation**: Gently relax your shoulders, unclench your jaw, and let your hands soften.\n\n"
                "What is one small sensation you can focus on right now?"
            )
        else:
            coping = (
                "Remember that whatever you are experiencing right now is valid, but you don't have to carry it all at once.\n\n"
                "Would you like to try a brief grounding breath with me, or simply talk through what's on your mind?"
            )

        note = "\n\n*(Note: To connect to live Google Gemini models, please set `GEMINI_API_KEY` in your `.env` file.)*" if not self._is_configured else ""
        return f"{intro}{coping}{note}"

gemini_service = GeminiService()
