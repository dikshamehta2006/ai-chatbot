#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "🌸 Starting Lumen Streamlit Interface on http://localhost:8501..."
export PYTHONPATH=.
./venv/bin/streamlit run frontend/app.py --server.port 8501 --server.headless true
