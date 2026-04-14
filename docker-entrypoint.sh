#!/bin/sh

set -e

echo "Starting Campus Runner Backend..."

# Wait for database to be ready (if using PostgreSQL)
if [ -n "$DATABASE_URL" ]; then
    echo "Checking database connection..."
    python -c "
import os
import time
from sqlalchemy import create_engine

db_url = os.getenv('DATABASE_URL')
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print('Database connection successful!')
            break
    except Exception as e:
        retry_count += 1
        if retry_count < max_retries:
            print(f'Waiting for database... ({retry_count}/{max_retries})')
            time.sleep(2)
        else:
            print(f'Database connection failed after {max_retries} retries')
            raise
"
fi

# Run migrations if needed
echo "Setting up database..."
python backend/init_db.py

echo "Starting application..."
exec python backend/app.py
