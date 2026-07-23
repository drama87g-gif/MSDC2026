# MSDC - admissions and infra setup

This branch adds the admissions core features and infra scaffolding:

- Database: PostgreSQL via docker-compose (fallback to sqlite for dev)
- Backend: Flask + SQLAlchemy + Flask-Migrate + JWT auth scaffold
- Frontend scaffold: react + i18n (to be added)
- Features added:
  - Patient create/list/detail
  - Patient photo upload
  - CSV import/export for patients
  - Pagination for list endpoints
  - Gunicorn as the production server

How to run locally (quick):

1. Ensure Docker is installed.
2. From the repo root run:

   docker compose up --build

3. The backend will be available at http://localhost:5000 and frontend dev at http://localhost:3000 (if frontend configured).

Notes:
- The first run will create DB tables because INIT_DB=1 in docker-compose environment for convenience. In production, remove INIT_DB and run `flask db upgrade` after applying migrations.
