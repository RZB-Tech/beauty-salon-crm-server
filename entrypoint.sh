#!/bin/sh
set -e

echo "Waiting for postgres"
sleep 10

echo "Running migrations"
uv run migrate.py

echo "Starting server"
exec uv run uvicorn src.app:app --host 0.0.0.0 --port 8000