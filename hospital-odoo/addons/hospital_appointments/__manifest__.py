{
    'name': 'Hospital Appointments',
    'version': '17.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Appointment scheduling and management',
    'author': 'Hospital Admin',
    'license': 'LGPL-3',
    'depends': ['hospital_core', 'calendar'],
    'data': [
        'security/ir.model.access.csv',
        'views/hospital_appointment_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
