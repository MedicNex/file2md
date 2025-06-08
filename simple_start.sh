#!/bin/bash
cd /www/wwwroot/medicnex-file2md
source venv/bin/activate
export AGENT_API_KEYS=${AGENT_API_KEYS:-"dev-test-key-123"}
export PORT=${PORT:-8999}
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
