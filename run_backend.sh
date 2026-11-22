#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "🌸 Starting Lumen FastAPI Backend on http://127.0.0.1:8000..."
export PYTHONPATH=.
./venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
