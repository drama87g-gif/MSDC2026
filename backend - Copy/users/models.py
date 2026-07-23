#=== FILE: backend/users/models.py ===
from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    department = models.CharField(max_length=64, blank=True)
    contact = models.CharField(max_length=64, blank=True)