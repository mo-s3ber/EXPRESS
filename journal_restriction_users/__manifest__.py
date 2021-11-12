# -*- coding: utf-8 -*-
{
    'name': "Journal Restriction Users",
    'summary': """
            Journal Restriction For Users
        """,
    'description': """
        Journal Restriction For Users
    """,
    'author': "Mohamed Saber",
    'category': 'Uncategorized',
    'version': '14.1',
    'depends': ['base','account_accountant','cash_register_payment'],
    'data': [
        'security/journal_security.xml',
        'views/account_journal_views.xml',
        'views/account_move.xml'
    ]
}
