#!/bin/bash
# Hister 2.0 - Backend Startup Script

cd /home/theo/Python/Hister_2/backend

echo "🚀 Starte Hister 2.0 Backend..."
echo "📡 Server: http://0.0.0.0:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""

./venv/bin/python3 -m uvicorn app.main:socket_app --host 0.0.0.0 --port 8000
