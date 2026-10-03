{
    'name': 'Nephro Portal',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'Patient portal for nephrology: sessions, bilans, appointments, prescriptions, invoices',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis', 'nephro_bilans', 'nephro_billing', 'website', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
}
