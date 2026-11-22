import os
import uuid
import requests
import streamlit as st
from pathlib import Path
from frontend.components.visual_cues import render_emergency_banner, render_grounding_toolkit

# Page configuration
st.set_page_config(
    page_title="Lumen | Multimodal Emotional Support",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration & Constants
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")

# Custom CSS for soothing emotional wellness aesthetic
st.markdown("""
<style>
    .main {
        background-color: #fafbfc;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .rag-badge {
        display: inline-block;
        background-color: #e8f4fd;
        color: #0b69a3;
        font-size: 0.8rem;
        padding: 3px 8px;
        border-radius: 12px;
        margin-right: 6px;
        margin-top: 6px;
    }
    .crisis-alert {
        background-color: #fde8e8;
        color: #9b1c1c;
        border-left: 4px solid #f05252;
        padding: 10px 14px;
        border-radius: 4px;
        margin-top: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "session_id" not in st.session_state:
    try:
        res = requests.post(f"{API_BASE_URL}/api/v1/session/new", timeout=3)
        if res.status_code == 200:
            st.session_state.session_id = res.json()["session_id"]
        else:
            st.session_state.session_id = f"sess_{uuid.uuid4().hex[:12]}"
    except Exception:
        st.session_state.session_id = f"sess_{uuid.uuid4().hex[:12]}"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "sender": "ASSISTANT",
            "text": "Hello, I'm **Lumen**, your multimodal companion. Whether you're feeling overwhelmed, anxious, or just need a safe space to breathe and share what's on your mind—I am here to listen with patience and zero judgment.\n\nYou can talk with me via text, upload a drawing or journal photo, or share a voice note.",
            "audio_url": None,
            "rag_sources": []
        }
    ]

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### 🌸 Lumen Companion")
    st.caption("A private, compassionate AI space for reflection, grounding, and distress tolerance.")
    
    st.divider()
    
    # Backend Status Check
    st.markdown("##### 🔌 System Status")
    try:
        health_res = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=2)
        if health_res.status_code == 200:
            data = health_res.json()
            db_dialect = data["database"]["dialect"].upper()
            st.success(f"Backend: Online | DB: {db_dialect} | RAG: Ready ({data['rag']['indexed_chunks']} chunks)")
            if data["gemini"]["status"] != "configured":
                st.info("💡 Note: Running with built-in RAG grounding. Add `GEMINI_API_KEY` to .env to activate live Gemini models.")
        else:
            st.warning("Backend responding with non-200 status.")
    except Exception:
        st.error(f"Cannot connect to FastAPI at `{API_BASE_URL}`. Make sure FastAPI server is running.")

    st.divider()
    
    # Quick Mood Check-in
    st.markdown("##### 💭 Quick Check-in")
    quick_moods = ["🌱 Seeking Calm", "⚡ Feeling Anxious", "🌧️ Feeling Down", "🤯 Overwhelmed", "🌊 Just Need to Vent"]
    selected_mood = st.selectbox("How is your heart feeling right now?", quick_moods)
    if st.button("Share Mood with Lumen"):
        prompt_text = f"I am feeling: {selected_mood}. Could you offer me a gentle reflection and a quick grounding thought?"
        st.session_state.pending_prompt = prompt_text
        st.rerun()

    st.divider()
    
    # Session Controls
    st.caption(f"Session ID: `{st.session_state.session_id}`")
    if st.button("🔄 Reset Conversation"):
        st.session_state.session_id = f"sess_{uuid.uuid4().hex[:12]}"
        st.session_state.messages = [
            {
                "sender": "ASSISTANT",
                "text": "A fresh page is open. Take a slow, deep breath. I am listening whenever you are ready.",
                "audio_url": None,
                "rag_sources": []
            }
        ]
        st.rerun()

# ----------------- MAIN UI -----------------
st.title("Lumen: Personal Emotional Support Companion")
render_emergency_banner()
render_grounding_toolkit()

# Display Conversation History
for msg in st.session_state.messages:
    if msg["sender"] == "USER":
        with st.chat_message("user", avatar="👤"):
            if msg.get("image"):
                st.image(msg["image"], caption="Attached Image", width=320)
            if msg.get("audio"):
                st.audio(msg["audio"])
            st.markdown(msg["text"])
    else:
        with st.chat_message("assistant", avatar="🌸"):
            st.markdown(msg["text"])
            if msg.get("audio_url"):
                full_audio_url = f"{API_BASE_URL}{msg['audio_url']}" if msg['audio_url'].startswith("/") else msg['audio_url']
                st.audio(full_audio_url)
            if msg.get("rag_sources"):
                rag_badges = " ".join([f"<span class='rag-badge'>📚 Grounded in: {s}</span>" for s in msg["rag_sources"]])
                st.markdown(rag_badges, unsafe_allow_html=True)
            if msg.get("is_crisis"):
                st.markdown("<div class='crisis-alert'>⚠️ Crisis safety protocol engaged. Emergency resources surfaced above.</div>", unsafe_allow_html=True)

# ----------------- MULTIMODAL INPUTS -----------------
with st.expander("📎 Attach Multimodal Media (Image or Audio)", expanded=False):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        uploaded_image = st.file_uploader(
            "Upload Image (Mood board, journal, sketch)",
            type=["png", "jpg", "jpeg", "webp"],
            key="img_uploader"
        )
        if uploaded_image:
            st.image(uploaded_image, width=160, caption="Preview")
            
    with col2:
        uploaded_audio = st.file_uploader(
            "Upload Voice Note (.wav, .mp3)",
            type=["wav", "mp3", "m4a", "ogg"],
            key="aud_uploader"
        )
        if uploaded_audio:
            st.audio(uploaded_audio)

    with col3:
        synthesize_audio = st.checkbox("🎙️ Voice Response (TTS)", value=True, help="Synthesizes spoken audio for assistant responses")

# Chat input prompt
user_chat_input = st.chat_input("Share what is on your mind or in your heart...")
pending_prompt = getattr(st.session_state, "pending_prompt", None)
if pending_prompt:
    user_chat_input = pending_prompt
    st.session_state.pending_prompt = None

if user_chat_input or uploaded_image or uploaded_audio:
    user_text = user_chat_input or ""
    
    # Append User Message to State
    user_msg_entry = {
        "sender": "USER",
        "text": user_text,
        "image": uploaded_image,
        "audio": uploaded_audio
    }
    st.session_state.messages.append(user_msg_entry)
    
    # Rerender user message immediately
    with st.chat_message("user", avatar="👤"):
        if uploaded_image:
            st.image(uploaded_image, caption="Attached Image", width=320)
        if uploaded_audio:
            st.audio(uploaded_audio)
        if user_text:
            st.markdown(user_text)

    # Prepare multipart request to FastAPI
    with st.chat_message("assistant", avatar="🌸"):
        with st.spinner("Lumen is listening and reflecting..."):
            try:
                files = {}
                if uploaded_image:
                    files["image"] = (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)
                if uploaded_audio:
                    files["audio"] = (uploaded_audio.name, uploaded_audio.getvalue(), uploaded_audio.type)

                data = {
                    "session_id": st.session_state.session_id,
                    "message": user_text,
                    "generate_audio": "true" if synthesize_audio else "false"
                }

                response = requests.post(
                    f"{API_BASE_URL}/api/v1/chat/message",
                    data=data,
                    files=files if files else None,
                    timeout=45
                )

                if response.status_code == 200:
                    res_data = response.json()
                    bot_text = res_data.get("response", "")
                    audio_url = res_data.get("audio_url")
                    rag_sources = res_data.get("rag_sources", [])
                    is_crisis = res_data.get("is_crisis", False)

                    st.markdown(bot_text)
                    if audio_url:
                        full_audio_url = f"{API_BASE_URL}{audio_url}" if audio_url.startswith("/") else audio_url
                        st.audio(full_audio_url)
                    if rag_sources:
                        rag_badges = " ".join([f"<span class='rag-badge'>📚 Grounded in: {s}</span>" for s in rag_sources])
                        st.markdown(rag_badges, unsafe_allow_html=True)

                    # Save to state
                    st.session_state.messages.append({
                        "sender": "ASSISTANT",
                        "text": bot_text,
                        "audio_url": audio_url,
                        "rag_sources": rag_sources,
                        "is_crisis": is_crisis
                    })
                else:
                    error_msg = f"Error from server ({response.status_code}): {response.text}"
                    st.error(error_msg)
            except Exception as req_err:
                st.error(f"Failed to communicate with Lumen backend: {req_err}")
