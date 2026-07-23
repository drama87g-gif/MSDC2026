{
    'name': 'Hospital Billing',
    'version': '17.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Patient billing and invoice management',
    'author': 'Hospital Admin',
    'license': 'LGPL-3',
    'depends': ['hospital_core', 'hospital_appointments', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/hospital_invoice_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
