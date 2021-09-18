# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2021 dev:Mohamed Saber.
#    E-Mail:mohamedabosaber94@gmail.com
#    Mobile:+201153909418
#
##############################################################################
{
    'name': 'Partner Statement',
    'version': '12.0.1',
    'summary': 'Module accounting reports for customer/vendor Statement.',
    'sequence': 16,
    'category': 'Account',
    'author': 'Mohamed Saber',
    'description': """
Custom Accounting Reports
=====================================
This module print Module accounting reports for customer/vendor Statement.
    """,
    "license": "AGPL-3",
    'depends': ['base_setup', 'account', 'account_accountant', 'reports_express'],
    'data': [
        'views/report_vendor_statement_view.xml',
        'views/report_customer_statement_view.xml',
        'views/vendor_statement_action.xml',
        'views/customer_statement_action.xml',
        'wizard/wiz_vendor_statement_view.xml',
        'wizard/wiz_customer_statement_view.xml',
        'wizard/partner_ledger_wizard_view.xml',
        'wizard/partner_ledger_total_wizard_view.xml',
        'wizard/partner_statement_t_view.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
