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
    'category': 'Accounting',
    'version': '15.1',
    'depends': ['base','account','account_accountant'],
    'data': [
        'security/journal_security.xml',
        'views/account_journal_views.xml',
        # 'views/account_move.xml'
    ]
}
