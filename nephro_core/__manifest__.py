{
    'name': 'Nephro Core',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'Core models for nephrology HMS: patient, physician, procedure, appointment, prescription',
    'author': 'As-Shafi Medical',
    'website': 'https://as-shafi.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'product', 'contacts'],
    'data': [
        'security/security.xml',
        'data/sequence_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
