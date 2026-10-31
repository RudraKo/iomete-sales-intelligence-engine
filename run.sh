#!/usr/bin/env bash
set -e

# The Living Sales Intelligence Engine - Startup Script
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

export PYTHONPATH="."
MODE="${1:-streamlit}"
PORT="${PORT:-8501}"

echo "=========================================================="
echo " Starting The Living Sales Intelligence Engine (IOMETE)"
echo " Core Pillars: Sovereign Lakehouse | Spark | Iceberg | K8s"
echo " Zero-Hallucination Guard: ENFORCED"
echo " Target Mode: ${MODE}"
echo "=========================================================="

if [ "$MODE" = "api" ]; then
    export APP_PORT="${PORT:-8000}"
    echo "Launching FastAPI Engine on http://0.0.0.0:${APP_PORT}..."
    exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT}" --reload
else
    echo "Launching Streamlit Sales Copilot on http://0.0.0.0:${PORT}..."
    exec streamlit run frontend/app.py --server.port "${PORT}" --server.address 0.0.0.0
fi
