#=== FILE: backend/users/admin.py ===
from django.contrib import admin
from .models import User, Role
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra', {'fields': ('role', 'department', 'contact')}),
    )