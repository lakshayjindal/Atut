#!/bin/bash
set -e

echo "--- Vivah Sutra Docker Entrypoint ---"

# Let Python handle DATABASE_URL parsing and DB readiness check
python3 << 'PYEOF'
import os, time, psycopg2

# Resolve database connection details from env
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and not os.environ.get("DB_HOST"):
    from urllib.parse import urlparse
    r = urlparse(DATABASE_URL)
    os.environ["DB_HOST"]   = r.hostname or "localhost"
    os.environ["DB_PORT"]   = str(r.port or 5432)
    os.environ["DB_NAME"]   = r.path.lstrip("/") or "VivahSutra"
    os.environ["DB_USER"]   = r.username or "VivahSutra"
    os.environ["DB_PASSWORD"] = r.password or "VivahSutra"

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "VivahSutra")
os.environ.setdefault("DB_USER", "VivahSutra")
os.environ.setdefault("DB_PASSWORD", "VivahSutra")

host = os.environ["DB_HOST"]
port = os.environ["DB_PORT"]

print(f"Waiting for PostgreSQL at {host}:{port}...")
while True:
    try:
        psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=host,
            port=port,
        ).close()
        break
    except Exception as e:
        print(f"  retrying... ({e})")
        time.sleep(1)
print("PostgreSQL is ready.")
PYEOF

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Daphne ASGI server on 0.0.0.0:${PORT:-8000}..."
exec daphne -b 0.0.0.0 -p "${PORT:-8000}" main.asgi:application
