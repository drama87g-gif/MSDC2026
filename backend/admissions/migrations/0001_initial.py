# Generated initial migration for admissions app

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_remove_user_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_number', models.CharField(max_length=32, unique=True)),
                ('barcode', models.CharField(max_length=64, unique=True)),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('national_id', models.CharField(blank=True, max_length=64)),
                ('nationality', models.CharField(blank=True, max_length=64)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=16)),
                ('address', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=32)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('medical_history', models.TextField(blank=True)),
                ('allergies', models.TextField(blank=True)),
                ('photo', models.FileField(blank=True, null=True, upload_to='patient_photos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
