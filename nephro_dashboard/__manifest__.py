{
    'name': 'Nephro Dashboard',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'OWL dashboards for doctor, nurse, and secretary',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis', 'nephro_bilans', 'nephro_complications', 'bus'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_actions.xml',
        'views/menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'nephro_dashboard/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
}
