#!/bin/sh
set -e

# Default values if env vars are not set
: "${POSTGRES_HOST:=db}"
: "${POSTGRES_PORT:=5432}"

echo "Waiting for Postgres at $POSTGRES_HOST:$POSTGRES_PORT..."

# simple Python TCP check loop (works without netcat)
until python - <<PY
import socket,sys
s=socket.socket()
s.settimeout(1)
try:
    s.connect(("$POSTGRES_HOST", int("$POSTGRES_PORT")))
    print("postgres reachable")
    sys.exit(0)
except Exception as e:
    print("postgres not reachable:", e)
    sys.exit(1)
PY
do
  sleep 1
done

echo "Postgres is up — running migrations"
python manage.py migrate --noinput

# optional: seed roles or initial data if you have a management command
# python manage.py seed_roles || true

echo "Starting Gunicorn"
exec gunicorn msdc_backend.wsgi:application --bind 0.0.0.0:8000 --workers 3