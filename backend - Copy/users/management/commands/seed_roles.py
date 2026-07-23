#=== FILE: backend/users/management/commands/seed_roles.py ===

from django.core.management.base import BaseCommand
from users.models import Role, User

class Command(BaseCommand):
    help = 'Seed default roles and admin user'

    def handle(self, *args, **options):
        roles = ['Admin', 'Admission', 'Reception', 'Clinic', 'Pharmacy', 'Lab', 'Inventory']
        for r in roles:
            Role.objects.get_or_create(name=r)
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'AdminPass123')
            admin.role = Role.objects.get(name='Admin')
            admin.save()
        self.stdout.write(self.style.SUCCESS('Seeded roles and admin user')) 