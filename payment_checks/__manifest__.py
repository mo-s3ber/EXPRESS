{
    'name': "Payment Checks",
    'author': 'Mohamed Saber',
    'category': 'Accounting',
    'summary': """Payment Checks""",
    'website': '',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '14.0.0.1',
    'depends': ['account_accountant','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/check_book_view.xml',
        'views/payment_check_view.xml',
        'views/account_payment.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
