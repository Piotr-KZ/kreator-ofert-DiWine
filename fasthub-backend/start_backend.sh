#!/bin/bash
# Startup script for AutoFlow backend
# Unsets Manus system env vars to use local .env instead

# Unset Manus environment variables that conflict with local .env
unset DATABASE_URL
unset REDIS_URL
unset REDIS_HOST
unset REDIS_PORT

# Start backend
cd /home/ubuntu/fasthub-backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
