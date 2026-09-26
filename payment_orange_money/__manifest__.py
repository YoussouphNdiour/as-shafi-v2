{
    'name': 'Payment Orange Money',
    'version': '19.0.2.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Orange Money payment provider with HMAC-signed webhooks — zero hidden fees',
    'author': 'As-Shafi Medical',
    'license': 'LGPL-3',
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
    ],
    'installable': True,
    'application': False,
}
