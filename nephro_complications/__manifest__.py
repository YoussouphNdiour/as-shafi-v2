{
    'name': 'Nephro Complications',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'Per-session dialysis complications tracking',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis'],
    'data': [
        'security/ir.model.access.csv',
        'views/complication_views.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
}
