{
    'name': 'Nephro Billing',
    'version': '19.0.2.0.0',
    'category': 'Healthcare',
    'summary': 'Dialysis pricing rules, auto-invoicing, batch invoicing, patient balance',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['nephro_dialysis', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/pricing_rule_views.xml',
        'views/patient_billing_views.xml',
        'views/uninvoiced_views.xml',
        'views/batch_invoice_views.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
}
