{
    'name': 'Hospital Pharmacy',
    'version': '17.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Pharmacy management - drug inventory and dispensing',
    'author': 'Hospital Admin',
    'license': 'LGPL-3',
    'depends': ['hospital_core', 'hospital_medical_records', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/hospital_medicine_views.xml',
        'views/hospital_dispensing_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
