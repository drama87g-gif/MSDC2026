# Build Configuration for PyInstaller
# This file contains build configurations for each desktop application

# Common options for all applications
common_options = {
    'icon': 'resources/app_icon.ico',
    'console': False,  # No console window
    'hiddenimports': [
        'PyQt5',
        'requests',
        'PIL',
        'reportlab',
        'dotenv'
    ]
}

# Application-specific configurations
applications = {
    'admin': {
        'name': 'Admin',
        'main_file': 'admin/main.py',
        'icon': 'resources/admin_icon.ico',
        'version': '3.0.0',
        'description': 'MSDC Hospital Admin Panel'
    },
    'admission': {
        'name': 'Admission',
        'main_file': 'admission/main.py',
        'icon': 'resources/admission_icon.ico',
        'version': '3.0.0',
        'description': 'MSDC Hospital Admission Department'
    },
    'reception': {
        'name': 'Reception',
        'main_file': 'reception/main.py',
        'icon': 'resources/reception_icon.ico',
        'version': '3.0.0',
        'description': 'MSDC Hospital Reception'
    },
    'pharmacy': {
        'name': 'Pharmacy',
        'main_file': 'pharmacy/main.py',
        'icon': 'resources/pharmacy_icon.ico',
        'version': '3.0.0',
        'description': 'MSDC Hospital Pharmacy'
    },
    'lab': {
        'name': 'Lab',
        'main_file': 'lab/main.py',
        'icon': 'resources/lab_icon.ico',
        'version': '3.0.0',
        'description': 'MSDC Hospital Laboratory'
    },
    'clinic': {
        'name': 'Clinic',
        'main_file': 'clinic/main.py',
        'icon': 'resources/clinic_icon.ico',
        'version': '3.0.0',
        'description': 'MSDC Hospital Clinic'
    },
    'medical_inventory': {
        'name': 'MedicalInventory',
        'main_file': 'medical_inventory/main.py',
        'icon': 'resources/inventory_icon.ico',
        'version': '3.0.0',
        'description': 'MSDC Medical Inventory Management'
    },
    'statistics': {
        'name': 'Statistics',
        'main_file': 'statistics/main.py',
        'icon': 'resources/stats_icon.ico',
        'version': '3.0.0',
        'description': 'MSDC Hospital Statistics & Reports'
    }
}

# Build commands for each application
build_commands = """
# Build all applications
pyinstaller --name Admin --icon=resources/admin_icon.ico --onefile --windowed admin/main.py
pyinstaller --name Admission --icon=resources/admission_icon.ico --onefile --windowed admission/main.py
pyinstaller --name Reception --icon=resources/reception_icon.ico --onefile --windowed reception/main.py
pyinstaller --name Pharmacy --icon=resources/pharmacy_icon.ico --onefile --windowed pharmacy/main.py
pyinstaller --name Lab --icon=resources/lab_icon.ico --onefile --windowed lab/main.py
pyinstaller --name Clinic --icon=resources/clinic_icon.ico --onefile --windowed clinic/main.py
pyinstaller --name MedicalInventory --icon=resources/inventory_icon.ico --onefile --windowed medical_inventory/main.py
pyinstaller --name Statistics --icon=resources/stats_icon.ico --onefile --windowed statistics/main.py
"""
