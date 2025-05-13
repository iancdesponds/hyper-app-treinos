#!/bin/bash
set -a
source .env
set +a

exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
