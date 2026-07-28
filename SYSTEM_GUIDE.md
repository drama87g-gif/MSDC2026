# MSDC 2026 - Hospital Management System v2.0

## ✨ New Features

### Database Enhancements
- ✅ **Department Management** - Multiple departments with staffing
- ✅ **User Authentication** - Role-based access (Admin, Doctor, Nurse, Receptionist, Patient)
- ✅ **Enhanced Patient Records** - Blood type, emergency contact, insurance info
- ✅ **Prescription Management** - Complete medication prescriptions
- ✅ **Billing System** - Invoice generation and payment tracking
- ✅ **Low Stock Alerts** - Automatic medication inventory alerts

### Backend Improvements
- ✅ **Flask-Admin Integration** - Complete admin panel for all entities
- ✅ **Department APIs** - Full CRUD operations
- ✅ **Prescription Management** - API endpoints for prescriptions
- ✅ **Invoice Management** - Billing API with payment tracking
- ✅ **Password Security** - Werkzeug password hashing
- ✅ **Department-specific Filtering** - Query appointments by department

### Frontend Components
- ✅ **Dashboard** - Real-time statistics and system health
- ✅ **Patients Interface** - Full patient management with filtering
- ✅ **Medications Inventory** - Stock level monitoring
- ✅ **Appointment Scheduling** - Queue management
- ✅ **Department Directory** - Hospital departments and contacts
- ✅ **Billing Interface** - Invoice tracking and payment status

## System Stack

- **Backend**: Flask 2.3 with SQLAlchemy ORM
- **Frontend**: React 18 with Vite bundler
- **Database**: PostgreSQL 15 with comprehensive schema
- **Admin**: Flask-Admin for database management
- **Authentication**: Flask-Login with role-based access

## Database Schema

### Core Tables
- `users` - Staff and admin accounts with roles
- `departments` - Hospital departments
- `patients` - Patient records with extended fields
- `medications` - Medication inventory
- `appointments` - Appointment scheduling
- `prescriptions` - Medication prescriptions
- `invoices` - Billing and payment tracking

## Quick Start

### Prerequisites
```bash
Docker & Docker Compose
Git
```

### Setup & Run

```bash
# Clone repository
git clone https://github.com/drama87g-gif/MSDC2026.git
cd MSDC2026

# Configure environment
cp .env.example .env

# Start all services
docker compose up -d

# Wait for database initialization (10-15 seconds)

# Access applications
Frontend: http://localhost
Admin Panel: http://localhost/admin
API Health: http://localhost/api/health
API Docs: Check README for endpoints
```

## Default Admin Credentials

```
Username: admin
Password: admin123
Role: admin
```

⚠️ **IMPORTANT**: Change these credentials immediately after first login!

## API Endpoints

### Health & System
- `GET /api/health` - System status

### Departments
- `GET /api/departments` - List all departments
- `POST /api/departments` - Create department
- `GET /api/departments/<id>` - Get department details
- `PUT /api/departments/<id>` - Update department
- `DELETE /api/departments/<id>` - Delete department

### Patients
- `GET /api/patients` - List patients (paginated)
- `POST /api/patients` - Create new patient
- `GET /api/patients/<id>` - Get patient details
- `PUT /api/patients/<id>` - Update patient
- `DELETE /api/patients/<id>` - Soft delete patient
- `POST /api/patients/<id>/photo` - Upload patient photo
- `GET /api/patients/export` - Export to CSV
- `POST /api/patients/import` - Import from CSV

### Medications
- `GET /api/medications` - List medications
- `POST /api/medications` - Create medication
- `GET /api/medications/<id>` - Get medication details
- `PUT /api/medications/<id>` - Update medication
- `DELETE /api/medications/<id>` - Delete medication
- `GET /api/medications/low-stock` - Get low stock items

### Appointments
- `GET /api/appointments` - List appointments (paginated)
- `POST /api/appointments` - Create appointment
- `GET /api/appointments/<id>` - Get appointment details
- `PUT /api/appointments/<id>` - Update appointment status
- `DELETE /api/appointments/<id>` - Cancel appointment

### Prescriptions
- `GET /api/prescriptions` - List prescriptions
- `GET /api/prescriptions?patient_id=<id>` - Get patient prescriptions
- `POST /api/prescriptions` - Create prescription

### Invoices
- `GET /api/invoices` - List invoices
- `GET /api/invoices?patient_id=<id>` - Get patient invoices
- `POST /api/invoices` - Create invoice
- `PUT /api/invoices/<id>` - Record payment

## Docker Services

```yaml
db       - PostgreSQL 15 (Port 5432)
backend  - Flask API (Port 5000)
frontend - React + Nginx (Port 80)
```

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

### Database Issues
```bash
# Check database status
docker compose ps db

# View database logs
docker compose logs db

# Reset database
docker compose down -v
docker compose up -d
```

### Backend Connection Issues
```bash
# Check backend logs
docker compose logs backend

# Verify API
curl http://localhost/api/health
```

### Frontend Build Issues
```bash
# Clear cache and rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Project Structure
```
.
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container
│   ├── uploads/            # Patient photo storage
│   └── README_BACKEND.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Styling
│   │   └── main.jsx        # Entry point
│   ├── public/             # Static assets
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── nginx.conf          # Nginx configuration
│   ├── Dockerfile          # Frontend container
│   └── .dockerignore
├── db_init.sql             # Database initialization
├── docker-compose.yml      # Docker Compose setup
├── .env                    # Environment variables
├── .env.example            # Example env file
└── README.md               # This file
```

## Features Map

| Feature | Status | Module |
|---------|--------|--------|
| Patient Management | ✅ | Frontend, Backend, DB |
| Departments | ✅ | Frontend, Backend, DB |
| Appointments | ✅ | Frontend, Backend, DB |
| Medications | ✅ | Frontend, Backend, DB |
| Prescriptions | ✅ | Backend, DB |
| Billing | ✅ | Frontend, Backend, DB |
| User Auth | ✅ | Backend, Admin |
| Admin Panel | ✅ | Backend (Flask-Admin) |
| Photo Upload | ✅ | Backend |
| CSV Import/Export | ✅ | Backend |
| Low Stock Alerts | ✅ | Frontend, Backend |

## Performance Considerations

- Database indexes on frequently queried fields
- Pagination for large datasets (default 25 per page)
- Connection pooling via SQLAlchemy
- Nginx gzip compression for frontend
- Static asset caching with far-future expires headers

## Security Considerations

- ⚠️ Change default admin password immediately
- Use strong DATABASE_URL in production
- Set unique SECRET_KEY in production
- Enable HTTPS in production
- Implement rate limiting for APIs
- Validate all user inputs
- Use environment variables for sensitive data

## License

MSDC 2026 - Hospital Management System
