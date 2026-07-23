=== FILE: backend/README_BACKEND.txt ===
Backend Notes
-------------
- API base: /api/
- Patient endpoints:
  GET /api/patients/
  POST /api/patients/
  GET /api/patients/{id}/
  PUT /api/patients/{id}/
  DELETE /api/patients/{id}/
  POST /api/patients/import/  (multipart form-data file)
  GET /api/patients/{id}/card/  (PDF)

- Authentication:
  POST /api/auth/token/  -> {username, password} returns access and refresh tokens
  Use Authorization: Bearer <access_token> for API calls.

- Media files are stored in backend/media by default and mapped to host via docker volume media_data.

Extending admissions:
- Add more fields to Patient model and run makemigrations.
- Add search endpoints and filters using DjangoFilterBackend.