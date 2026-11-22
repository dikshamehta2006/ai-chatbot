# Lumen: Multimodal Emotional Support AI Chatbot

A secure, compassionate, multimodal conversational AI companion grounded in psychological first-aid literature (CBT, DBT, Mindfulness) using Retrieval-Augmented Generation (RAG), powered by the **Google Gemini** model family.

---

## 🌟 Key Features

1. **Multimodal Inputs & Outputs**:
   - **Text Prompts**: Conversational empathy, reflective listening, and cognitive reframing.
   - **Image Understanding**: Upload mood boards, drawings, art sketches, or handwritten journal entries.
   - **Audio / Voice Processing**: Upload voice notes or listen to synthesized spoken audio responses (`.wav`/`.mp3`).
   - **Visual Grounding Tools**: Guided Box Breathing (4x4), 5-4-3-2-1 Sensory Grounding, and DBT STOP skills.

2. **Defined Multi-Ring Guardrails**:
   - **Ring 1: PII Scrubbing**: Automatic redacting of phone numbers, email addresses, credit cards, and SSNs.
   - **Ring 2: Crisis & Self-Harm Red-Flag Protocol**: Immediate detection of self-harm or acute distress cues, instantly surfacing verified 24/7 crisis hotlines (988, Tele-MANAS 14416, 741741, 116 123) and logging to audit logs.
   - **Ring 3: Output Safety & Anti-Diagnosis Verification**: Prevents medical prescription or formal psychiatric diagnosis from leaking into responses.

3. **Domain RAG Architecture**:
   - Curated knowledge repository under `knowledge_docs/` (CBT Thought Records, DBT Distress Tolerance, Somatic Breathing, Emergency Helplines).
   - Embedding & similarity retrieval via Gemini `text-embedding-004` (with lexical fallback for zero-network environments).

4. **Tech Stack**:
   - **API Backend**: FastAPI with async route handlers, file ingestion, and CORS middleware.
   - **Frontend Replacement**: Streamlit interactive web application with chat bubbles, media uploaders, audio player, and quick mood check-ins.
   - **Database**: MySQL with SQLAlchemy ORM (auto-detects MySQL; gracefully falls back to local SQLite if MySQL server is offline).
   - **LLM**: Google Gemini (`gemini-2.5-flash` / `gemini-1.5-flash`).

---

## 📁 Project Architecture

```
ai-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── chat.py          # Multimodal chat & guardrail execution
│   │   │   │   ├── session.py       # Session management
│   │   │   │   └── health.py        # System health & DB status check
│   │   │   └── routes.py            # API v1 aggregator
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic environment settings
│   │   │   ├── guardrails.py        # Crisis detection, PII masking & audit
│   │   │   └── prompts.py           # Master System Prompt ("Lumen")
│   │   ├── db/
│   │   │   ├── database.py          # MySQL / SQLite SQLAlchemy connection
│   │   │   ├── init_db.py           # Standalone DB creator script
│   │   │   └── models.py            # Sessions, ChatMessages, SafetyAuditLogs
│   │   ├── rag/
│   │   │   ├── vector_store.py      # Markdown chunker & similarity search
│   │   │   └── retriever.py         # Prompt context injector
│   │   ├── services/
│   │   │   ├── gemini_service.py    # Google Gemini multimodal integration
│   │   │   └── audio_service.py     # TTS speech synthesis (.wav / .mp3)
│   │   └── main.py                  # FastAPI application entrypoint
├── frontend/
│   ├── app.py                       # Streamlit interactive UI
│   └── components/
│       └── visual_cues.py           # Crisis banner & Grounding toolkit tabs
├── knowledge_docs/                  # Curated therapeutic knowledge base
│   ├── cbt_reframing.md
│   ├── dbt_distress_tolerance.md
│   ├── mindfulness_and_breathing.md
│   └── crisis_safety_protocols.md
├── tests/
│   ├── test_guardrails.py           # Unit tests for safety & PII
│   ├── test_rag.py                  # RAG indexing & retrieval tests
│   └── test_api.py                  # FastAPI endpoint integration tests
├── .env.example
├── requirements.txt
├── run_backend.sh
├── run_frontend.sh
└── start.sh
```

---

## 🚀 Quickstart Guide

### 1. Configure Environment
Edit `.env` (copied from `.env.example`):
```env
# Add your Gemini API key (from https://aistudio.google.com)
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Optional MySQL Configuration (if running a local MySQL server)
MYSQL_HOST="localhost"
MYSQL_PORT=3306
MYSQL_USER="root"
MYSQL_PASSWORD="your_password"
MYSQL_DATABASE="emotional_support_db"
```

### 2. Launch the Application
You can run the full system using the all-in-one launcher:
```bash
./start.sh
```

Or launch services independently in separate terminal windows:
- **Terminal 1 (Backend)**:
  ```bash
  ./run_backend.sh
  ```
  FastAPI will be available at `http://localhost:8000` (Interactive docs: `http://localhost:8000/docs`).

- **Terminal 2 (Frontend)**:
  ```bash
  ./run_frontend.sh
  ```
  Streamlit interface will open at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the full test suite verifying guardrails, RAG retrieval, and FastAPI endpoints:
```bash
PYTHONPATH=. ./venv/bin/python tests/test_guardrails.py
PYTHONPATH=. ./venv/bin/python tests/test_rag.py
PYTHONPATH=. ./venv/bin/python tests/test_api.py
```
