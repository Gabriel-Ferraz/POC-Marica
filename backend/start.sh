#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding initial data..."
python -m app.db.seed

echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
