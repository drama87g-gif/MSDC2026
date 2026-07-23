#=== FILE: backend/admissions/middleware.py ===
import json
from .models import Patient
from users.models import User
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.conf import settings
from django.db import models

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=64)
    entity = models.CharField(max_length=64)
    entity_id = models.IntegerField(null=True)
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

class AuditMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        try:
            user = getattr(request, 'user', None)
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and request.path.startswith('/api/'):
                # Basic audit entry
                AuditLog.objects.create(
                    user=user if user and user.is_authenticated else None,
                    action=request.method,
                    entity=request.path,
                    entity_id=None,
                    details={'path': request.path, 'body': request.body.decode('utf-8', errors='ignore')[:1000]}
                )
        except Exception:
            pass
        return response