#=== FILE: backend/admissions/serializers.py ==
from rest_framework import serializers
from .models import Patient
from django.core.files.base import ContentFile
import base64
import uuid

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        # Ensure barcode and file_number exist
        if not validated_data.get('file_number'):
            validated_data['file_number'] = str(uuid.uuid4())[:12]
        if not validated_data.get('barcode'):
            validated_data['barcode'] = str(uuid.uuid4())[:12]
        return super().create(validated_data)