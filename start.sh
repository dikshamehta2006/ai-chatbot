#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🌸 Launching Lumen: Multimodal Emotional Support Companion"
echo "=========================================================="

# Start backend in background
export PYTHONPATH=.
echo "Starting FastAPI backend on port 8000..."
./venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

trap "echo 'Stopping Lumen services...'; kill $BACKEND_PID; exit 0" SIGINT SIGTERM

sleep 2

# Start frontend
echo "Starting Streamlit frontend on port 8501..."
./venv/bin/streamlit run frontend/app.py --server.port 8501 --server.headless true

wait $BACKEND_PID
