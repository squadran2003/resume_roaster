#!/bin/bash
set -e

# Use venv binaries directly if they exist (Railway/Nixpacks)
if [ -d /app/.venv/bin ]; then
    export PATH="/app/.venv/bin:$PATH"
fi

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Celery worker..."
    exec celery -A config.celery worker --loglevel=info --concurrency=2
else
    echo "Running migrations..."
    python manage.py migrate --noinput
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    echo "Starting web server..."
    exec gunicorn config.asgi:application -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
fi
