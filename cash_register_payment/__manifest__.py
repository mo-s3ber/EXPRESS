{
    'name': "Payment Cash Register",
    'author': 'Mohamed Saber',
    'category': 'Accounting',
    'summary': """Payment Cash Register """,
    'website': '',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '14.0.0.1',
    'depends': ['account_accountant','account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
