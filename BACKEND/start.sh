#!/bin/bash
# start.sh
set -e

# Run database migrations
echo "Running database migrations..."
alembic -c migrations/alembic.ini upgrade head

# Initialize database
echo "Initializing database..."
python scripts/init_db.py

# Start the application
echo "Starting backend server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
