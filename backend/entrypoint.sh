#!/bin/sh
set -e

# Wait for DB to be ready
echo "Waiting for database..."
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${POSTGRES_USER:-postgres}"; do
  sleep 1
done

# Make migrations for the users app first (safe if migrations already exist)
python manage.py makemigrations users || true
python manage.py migrate users --noinput || true

# Run all remaining migrations
python manage.py migrate --noinput

# Collect static (optional)
# python manage.py collectstatic --noinput

# Exec the container's main process
exec "$@"