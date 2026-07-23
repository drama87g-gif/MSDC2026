#=== FILE: backend/admissions/views.py ===

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
import openpyxl

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer
    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=['post'], url_path='import')
    def import_patients(self, request):
        """
        Accepts an uploaded .xlsx file under 'file' form field.
        Returns summary of created and failed rows.
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=400)
        wb = openpyxl.load_workbook(file_obj)
        sheet = wb.active
        created = 0
        failed = 0
        errors = []
        headers = [cell.value for cell in sheet[1]]
        for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            data = dict(zip(headers, row))
            try:
                patient_data = {
                    'first_name': data.get('first_name') or '',
                    'last_name': data.get('last_name') or '',
                    'national_id': str(data.get('national_id') or ''),
                    'file_number': str(data.get('file_number') or ''),
                    'barcode': str(data.get('barcode') or ''),
                    'date_of_birth': data.get('date_of_birth'),
                    'phone': str(data.get('phone') or ''),
                    'email': data.get('email') or '',
                    'nationality': data.get('nationality') or '',
                    'address': data.get('address') or '',
                    'medical_history': data.get('medical_history') or '',
                    'allergies': data.get('allergies') or '',
                }
                serializer = PatientSerializer(data=patient_data)
                if serializer.is_valid():
                    serializer.save()
                    created += 1
                else:
                    failed += 1
                    errors.append({'row': idx, 'errors': serializer.errors})
            except Exception as e:
                failed += 1
                errors.append({'row': idx, 'errors': str(e)})
        return Response({'created': created, 'failed': failed, 'errors': errors})

    @action(detail=True, methods=['get'], url_path='card')
    def card(self, request, pk=None):
        """
        Generate a simple PDF patient card for printing.
        """
        patient = self.get_object()
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=(288, 432))  # 3.5in x 5in approx
        p.setFont("Helvetica-Bold", 14)
        p.drawString(20, 380, "MSDC Patient Card")
        p.setFont("Helvetica", 12)
        p.drawString(20, 350, f"Name: {patient.first_name} {patient.last_name}")
        p.drawString(20, 330, f"National ID: {patient.national_id or ''}")
        p.drawString(20, 310, f"File No: {patient.file_number}")
        p.drawString(20, 290, f"Phone: {patient.phone or ''}")
        p.drawString(20, 270, f"Nationality: {patient.nationality or ''}")
        p.drawString(20, 240, "Barcode:")
        # Placeholder barcode rectangle
        p.rect(20, 200, 200, 30, stroke=1, fill=0)
        p.drawString(25, 205, patient.barcode or '')
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=patient_{patient.id}_card.pdf'
        return response