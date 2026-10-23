#!/bin/sh
python -c "
import time, psycopg2, os
url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/research')
for _ in range(30):
    try:
        psycopg2.connect(url).close()
        break
    except Exception:
        print('Waiting for postgres...')
        time.sleep(2)
"
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
