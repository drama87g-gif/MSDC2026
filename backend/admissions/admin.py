#=== FILE: backend/admissions/admin.py ===
from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('file_number', 'first_name', 'last_name', 'national_id', 'phone', 'created_at')
    search_fields = ('first_name', 'last_name', 'national_id', 'file_number', 'barcode')