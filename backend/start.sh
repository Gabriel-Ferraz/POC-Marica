#!/bin/bash
set -e

echo "Creating database tables..."
python -m app.db.create_tables

echo "Seeding initial data..."
python -m app.db.seed

echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
