{
    'name': 'Hospital Core',
    'version': '17.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Core hospital management - patients, doctors, departments',
    'author': 'Hospital Admin',
    'license': 'LGPL-3',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/hospital_patient_views.xml',
        'views/hospital_doctor_views.xml',
        'views/hospital_department_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
