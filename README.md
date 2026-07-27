# MSDC 2026 - Hospital Management System

A comprehensive hospital management system with patient management, medication inventory, and appointment scheduling.

## System Architecture

- **Backend**: Flask REST API with PostgreSQL
- **Frontend**: React with Vite
- **Database**: PostgreSQL 15
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/drama87g-gif/MSDC2026.git
cd MSDC2026
```

### 2. Configure environment variables
```bash
cp .env.example .env
# Edit .env if needed (defaults are provided)
```

### 3. Start the application
```bash
docker compose up -d
```

The application will be available at:
- **Frontend**: http://localhost
- **Backend API**: http://localhost/api
- **Health Check**: http://localhost/api/health

### 4. View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### 5. Stop the application
```bash
docker compose down
```

## Database

Tables are created automatically on first run. The system includes:

- **patients**: Patient records with personal and medical information
- **medications**: Medication inventory management
- **appointments**: Appointment scheduling and tracking

## API Endpoints

### Health Check
- `GET /api/health` - System status

### Patients
- `GET /api/patients` - List patients (paginated)
- `POST /api/patients` - Create new patient
- `GET /api/patients/<id>` - Get patient details
- `PUT /api/patients/<id>` - Update patient
- `DELETE /api/patients/<id>` - Delete patient
- `POST /api/patients/<id>/photo` - Upload patient photo
- `GET /api/patients/export` - Export patients to CSV
- `POST /api/patients/import` - Import patients from CSV

### Medications
- `GET /api/medications` - List medications (paginated)
- `POST /api/medications` - Create new medication

### Appointments
- `GET /api/appointments` - List appointments (paginated)
- `POST /api/appointments` - Create new appointment

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL=postgresql://msdc_user:msdc_pass@localhost:5432/msdc
python app.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Troubleshooting

### Database connection refused
- Ensure PostgreSQL container is running: `docker compose ps`
- Check logs: `docker compose logs db`
- Verify DATABASE_URL environment variable

### Frontend not loading
- Check if backend is running: `docker compose logs backend`
- Verify API connection: `curl http://localhost/api/health`
- Check nginx configuration: `docker compose logs frontend`

### Port already in use
- Change ports in docker-compose.yml or .env
- Or stop conflicting services: `docker compose down`

## Project Structure
```
.
├── backend/
│   ├── app.py              # Flask application
│   ├── Dockerfile          # Backend Docker image
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # Patient photo storage
├── frontend/
│   ├── src/                # React source code
│   ├── Dockerfile          # Frontend Docker image
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Docker Compose configuration
├── .env                    # Environment variables
└── README.md               # This file
```

## License

MSDC 2026
