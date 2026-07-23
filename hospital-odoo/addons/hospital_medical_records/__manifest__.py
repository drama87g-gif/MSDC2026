{
    'name': 'Hospital Medical Records',
    'version': '17.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Electronic Medical Records (EMR) management',
    'author': 'Hospital Admin',
    'license': 'LGPL-3',
    'depends': ['hospital_core', 'hospital_appointments'],
    'data': [
        'security/ir.model.access.csv',
        'views/hospital_medical_record_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
