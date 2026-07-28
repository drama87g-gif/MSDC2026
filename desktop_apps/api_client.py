import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """HTTP Client for communicating with Flask backend"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.auth_token = None
        self.user_info = None
    
    def set_auth_token(self, token: str):
        """Set authentication token for subsequent requests"""
        self.auth_token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and get token"""
        try:
            response = self.post('/api/auth/login', {
                'username': username,
                'password': password
            })
            if response.get('access_token'):
                self.set_auth_token(response['access_token'])
                self.user_info = response.get('user')
            return response
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise
    
    def logout(self):
        """Clear authentication"""
        self.auth_token = None
        self.user_info = None
        self.session.headers.pop('Authorization', None)
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GET {endpoint} failed: {str(e)}")
            raise
    
    def post(self, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        """POST request"""
        url = f"{self.base_url}{endpoint}"
        try:
            if files:
                # Don't use JSON for file uploads
                response = self.session.post(url, data=data, files=files, timeout=self.timeout)
            else:
                response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"POST {endpoint} failed: {str(e)}")
            raise
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT request"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.put(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"PUT {endpoint} failed: {str(e)}")
            raise
    
    def delete(self, endpoint: str) -> bool:
        """DELETE request"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"DELETE {endpoint} failed: {str(e)}")
            raise
    
    def check_health(self) -> bool:
        """Check API health"""
        try:
            response = self.get('/api/health')
            return response.get('status') == 'ok'
        except Exception:
            return False
    
    # ==================== ADMISSION DEPARTMENT ====================
    
    def get_patients(self, page: int = 1, per_page: int = 25) -> Dict:
        """Get paginated patient list"""
        return self.get('/api/admission/patients', {'page': page, 'per_page': per_page})
    
    def create_patient(self, patient_data: Dict) -> Dict:
        """Create new patient"""
        return self.post('/api/admission/patients', patient_data)
    
    def search_patient(self, query: str, search_type: str = 'name') -> Dict:
        """Search patient by name, barcode, or national ID"""
        return self.get('/api/admission/patients/search', {'q': query, 'type': search_type})
    
    def get_patient(self, patient_id: int) -> Dict:
        """Get patient details"""
        return self.get(f'/api/admission/patients/{patient_id}')
    
    def update_patient(self, patient_id: int, patient_data: Dict) -> Dict:
        """Update patient information"""
        return self.put(f'/api/admission/patients/{patient_id}', patient_data)
    
    def upload_patient_photo(self, patient_id: int, file_path: str) -> Dict:
        """Upload patient photo"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self.post(f'/api/admission/patients/{patient_id}/photo', files=files)
    
    def export_patients(self) -> bytes:
        """Export patients to CSV"""
        response = self.session.get(f"{self.base_url}/api/admission/patients/export", timeout=self.timeout)
        response.raise_for_status()
        return response.content
    
    def import_patients(self, file_path: str) -> Dict:
        """Import patients from CSV"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self.post('/api/admission/patients/import', files=files)
    
    # ==================== PATIENT FILE ====================
    
    def get_patient_files(self, patient_id: int) -> Dict:
        """Get patient files"""
        return self.get(f'/api/patient-files/by-patient/{patient_id}')
    
    def create_patient_file(self, file_data: Dict) -> Dict:
        """Create patient file"""
        return self.post('/api/patient-files', file_data)
    
    def update_patient_file(self, file_id: int, file_data: Dict) -> Dict:
        """Update patient file"""
        return self.put(f'/api/patient-files/{file_id}', file_data)
    
    def delete_patient_file(self, file_id: int) -> bool:
        """Delete patient file"""
        return self.delete(f'/api/patient-files/{file_id}')
    
    # ==================== RECEPTION DEPARTMENT ====================
    
    def get_appointments(self, page: int = 1, per_page: int = 25) -> Dict:
        """Get paginated appointments"""
        return self.get('/api/reception/appointments', {'page': page, 'per_page': per_page})
    
    def create_appointment(self, appointment_data: Dict) -> Dict:
        """Create appointment"""
        return self.post('/api/reception/appointments', appointment_data)
    
    def confirm_appointment(self, appointment_id: int) -> Dict:
        """Confirm appointment"""
        return self.post(f'/api/reception/appointments/{appointment_id}/confirm')
    
    def print_appointment(self, appointment_id: int) -> Dict:
        """Print appointment ticket (A5)"""
        return self.post(f'/api/reception/appointments/{appointment_id}/print')
    
    # ==================== LAB TESTS ====================
    
    def get_lab_tests(self, patient_id: Optional[int] = None, page: int = 1) -> Dict:
        """Get lab tests"""
        params = {'page': page}
        if patient_id:
            params['patient_id'] = patient_id
        return self.get('/api/lab/tests', params)
    
    def create_lab_test(self, test_data: Dict) -> Dict:
        """Create lab test"""
        return self.post('/api/lab/tests', test_data)
    
    def mark_sample_taken(self, test_id: int) -> Dict:
        """Mark sample as taken"""
        return self.post(f'/api/lab/tests/{test_id}/sample-taken')
    
    def update_lab_test_result(self, test_id: int, result_data: Dict) -> Dict:
        """Update lab test result"""
        return self.put(f'/api/lab/tests/{test_id}/results', result_data)
    
    # ==================== PHARMACY ====================
    
    def get_medications(self, page: int = 1) -> Dict:
        """Get medications"""
        return self.get('/api/pharmacy/medications', {'page': page})
    
    def create_medication(self, med_data: Dict) -> Dict:
        """Create medication"""
        return self.post('/api/pharmacy/medications', med_data)
    
    def get_low_stock_medications(self) -> Dict:
        """Get low stock medications"""
        return self.get('/api/pharmacy/medications/low-stock')
    
    def get_expiring_medications(self) -> Dict:
        """Get medications expiring soon"""
        return self.get('/api/pharmacy/medications/expiring-soon')
    
    def get_prescriptions(self, status: str = 'new') -> Dict:
        """Get prescriptions"""
        return self.get('/api/pharmacy/prescriptions', {'status': status})
    
    def dispense_prescription(self, prescription_id: int, dispense_data: Dict) -> Dict:
        """Dispense prescription"""
        return self.post(f'/api/pharmacy/prescriptions/{prescription_id}/dispense', dispense_data)
    
    def pharmacy_sale(self, sale_data: Dict) -> Dict:
        """Record pharmacy sale"""
        return self.post('/api/pharmacy/sales', sale_data)
    
    # ==================== CLINIC ====================
    
    def clinic_confirm_appointment(self, appointment_id: int) -> Dict:
        """Confirm appointment in clinic"""
        return self.post(f'/api/clinic/appointments/{appointment_id}/confirm')
    
    def create_diagnosis(self, diagnosis_data: Dict) -> Dict:
        """Create patient diagnosis"""
        return self.post('/api/clinic/diagnoses', diagnosis_data)
    
    def issue_prescription(self, prescription_data: Dict) -> Dict:
        """Issue prescription from clinic"""
        return self.post('/api/clinic/prescriptions', prescription_data)
    
    # ==================== STATISTICS ====================
    
    def get_patient_stats(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get patient registration statistics"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.get('/api/stats/patients/registered', params)
    
    def get_medication_stats(self, start_date: Optional[str] = None, end_date: Optional[str] = None, medication_id: Optional[int] = None) -> Dict:
        """Get medication sales statistics"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if medication_id:
            params['medication_id'] = medication_id
        return self.get('/api/stats/medications/sold', params)
    
    def get_lab_stats(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get lab test statistics"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.get('/api/stats/lab/tests', params)
    
    # ==================== SUPPLIERS ====================
    
    def get_suppliers(self) -> Dict:
        """Get all suppliers"""
        return self.get('/api/suppliers')
    
    def create_supplier(self, supplier_data: Dict) -> Dict:
        """Create new supplier"""
        return self.post('/api/suppliers', supplier_data)
    
    def update_supplier(self, supplier_id: int, supplier_data: Dict) -> Dict:
        """Update supplier"""
        return self.put(f'/api/suppliers/{supplier_id}', supplier_data)
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """Delete supplier"""
        return self.delete(f'/api/suppliers/{supplier_id}')
    
    # ==================== DEPARTMENTS ====================
    
    def get_departments(self) -> Dict:
        """Get all departments"""
        return self.get('/api/departments')
    
    def create_department(self, dept_data: Dict) -> Dict:
        """Create department"""
        return self.post('/api/departments', dept_data)
    
    def update_department(self, dept_id: int, dept_data: Dict) -> Dict:
        """Update department"""
        return self.put(f'/api/departments/{dept_id}', dept_data)
