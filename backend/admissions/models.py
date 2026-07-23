#=== FILE: backend/admissions/models.py ===

from django.db import models
from django.utils import timezone

class Patient(models.Model):
    file_number = models.CharField(max_length=32, unique=True)
    barcode = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    national_id = models.CharField(max_length=64, blank=True)
    nationality = models.CharField(max_length=64, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=16, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    medical_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    photo = models.FileField(upload_to='patient_photos/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.file_number})"