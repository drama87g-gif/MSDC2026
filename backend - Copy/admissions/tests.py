#=== FILE: backend/admissions/tests.py ===
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import Role, User
from .models import Patient
import io
from openpyxl import Workbook

class PatientTests(TestCase):
    def setUp(self):
        Role.objects.create(name='Admin')
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'AdminPass123')
        self.client = APIClient()
        # Obtain JWT token
        resp = self.client.post('/api/auth/token/', {'username': 'admin', 'password': 'AdminPass123'}, format='json')
        self.token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_patient(self):
        data = {'first_name': 'Test', 'last_name': 'Patient', 'file_number': 'F123', 'barcode': 'B123'}
        resp = self.client.post('/api/patients/', data, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Patient.objects.count(), 1)

    def test_update_patient(self):
        p = Patient.objects.create(first_name='A', last_name='B', file_number='F1', barcode='B1')
        resp = self.client.put(f'/api/patients/{p.id}/', {'first_name': 'Updated', 'last_name': 'B', 'file_number': 'F1', 'barcode': 'B1'}, format='json')
        self.assertEqual(resp.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.first_name, 'Updated')

    def test_delete_patient(self):
        p = Patient.objects.create(first_name='A', last_name='B', file_number='F2', barcode='B2')
        resp = self.client.delete(f'/api/patients/{p.id}/')
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Patient.objects.count(), 0)

    def test_import_patients(self):
        wb = Workbook()
        ws = wb.active
        headers = ['first_name','last_name','national_id','file_number','barcode','date_of_birth','phone','email','nationality','address','medical_history','allergies']
        ws.append(headers)
        ws.append(['Imp','One','NID1','FIMP1','BIMP1',None,'123','imp1@example.com','Libya','Addr1','Hist1','None'])
        ws.append(['Imp','Two','NID2','FIMP2','BIMP2',None,'456','imp2@example.com','Libya','Addr2','Hist2','None'])
        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        resp = self.client.post('/api/patients/import/', {'file': stream}, format='multipart')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Patient.objects.count(), 2)