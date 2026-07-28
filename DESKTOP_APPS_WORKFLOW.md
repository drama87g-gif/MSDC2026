# MSDC 2026 - Desktop Application Workflow

## Architecture Overview

The system consists of a centralized Flask API backend with 8 independent desktop applications (EXE files) that communicate with the database through REST APIs.

```
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database (Centralized)           │
└────────────────┬────────────────┬─────────────┬──────────────┘
                 │                │             │
         ┌───────▼─────────┐      │             │
         │  Flask REST API │◄─────┴─────────────┴──────┐
         │  (Backend)      │                           │
         └───────┬─────────┘                           │
                 │                                     │
    ┌────────────┼────────────────┬──────────────┬────┴─────────┐
    │            │                │              │              │
    ▼            ▼                ▼              ▼              ▼
┌─────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ Admin   │ │Admission │ │  Reception   │ │Pharmacy  │ │   Lab        │
│ .exe    │ │ .exe     │ │   .exe       │ │ .exe     │ │  .exe        │
└─────────┘ └──────────┘ └──────────────┘ └──────────┘ └──────────────┘
    │            │                │              │              │
    │            │                │              │              │
    ▼            ▼                ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│         All Applications Use Common HTTP Client API          │
└─────────────────────────────────────────────────────────────┘
```

## Development Workflow

### Phase 1: Backend Preparation ✅
1. **Flask REST API** - Already implemented
   - 60+ endpoints
   - Database models
   - Authentication
   - CORS enabled

### Phase 2: Create Python Desktop App Framework

We'll use **PyQt5** for the desktop UI and **requests** library for API communication.

#### Installation Dependencies
```bash
pip install PyQt5 requests pyinstaller python-dotenv pillow reportlab
```

### Phase 3: Build Each Application

Each application follows this structure:
```
App_Name/
├── main.py                 # Entry point
├── config.py              # API configuration
├── api_client.py          # HTTP client
├── ui/
│   ├── main_window.py     # Main UI
│   ├── login_dialog.py    # Authentication
│   └── widgets/           # Reusable components
├── models/                # Data models
├── services/              # Business logic
├── utils/                 # Helpers
├── resources/             # Icons, styles
└── build_exe.py           # PyInstaller config
```

### Phase 4: Build EXE Files

```bash
# Admin Application
pyinstaller --name Admin --icon=icon.ico admin/main.py

# Admission Application  
pyinstaller --name Admission --icon=icon.ico admission/main.py

# Reception Application
pyinstaller --name Reception --icon=icon.ico reception/main.py

# Pharmacy Application
pyinstaller --name Pharmacy --icon=icon.ico pharmacy/main.py

# Lab Application
pyinstaller --name Lab --icon=icon.ico lab/main.py

# Clinic Application
pyinstaller --name Clinic --icon=icon.ico clinic/main.py

# Medical Inventory Application
pyinstaller --name MedicalInventory --icon=icon.ico medical_inventory/main.py

# Statistics Application
pyinstaller --name Statistics --icon=icon.ico statistics/main.py
```

## Deployment

1. **Backend Server** - Deploy Flask app to cloud/server
2. **Database** - PostgreSQL on server
3. **Desktop Apps** - Distribute .exe files to departments
4. **Configuration** - Each .exe connects via IP/URL

## Communication Flow

Example: Admission App → Backend → Database

```
1. User opens Admission.exe
2. Logs in with credentials
3. Makes request: GET /api/admission/patients
4. API_CLIENT sends HTTP request to Flask backend
5. Flask queries PostgreSQL
6. Returns JSON response
7. Admission app parses and displays
8. User can CRUD patient records
9. All changes sync to central database
```

## Features Per Application

### Admin.exe
- User management
- Department configuration
- System settings
- Database monitoring
- Audit logs

### Admission.exe
- Register new patients
- Create patient files
- Upload photos
- Print patient cards
- View analytics

### Reception.exe
- Barcode scanner integration
- Create appointments
- Queue management
- Print A5 tickets
- Patient lookup

### Pharmacy.exe
- Medication inventory
- Prescription dispensing
- Sales interface
- Low stock alerts
- Print receipts

### Lab.exe
- Lab test management
- Sample tracking
- Result entry
- Print A4 reports
- Statistics

### Clinic.exe
- Appointment confirmation
- Diagnosis entry
- Prescription issuance
- Lab result review
- Patient history

### MedicalInventory.exe
- Supplier management
- Purchase orders
- Stock tracking
- Supply distribution
- Barcode scanning

### Statistics.exe
- Patient analytics
- Medication reports
- Lab statistics
- Revenue tracking
- Custom date ranges

## Next Steps

Would you like me to:
1. Create the common API client module (api_client.py)?
2. Build the base PyQt5 application framework?
3. Implement Admin.exe first as template?
4. Create the build/packaging workflow?
5. All of the above?
