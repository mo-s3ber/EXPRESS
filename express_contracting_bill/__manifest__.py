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
    'name': "Express Contracting Bills",

    'summary': """
    Express Contracting Bills management"
        """,

    'description': """
   Express Contracting Bills management
    """,

    'author': "Mohamed Saber",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': "12.0.0.1",

    # any module necessary for this one to work correctly
    'depends': ['base','mail','account','account_accountant'],

    # always loaded
    'data': [

        'views/contracting_bill_view.xml',
        'report/contracting_bill_report_view.xml',
        'report/contracting_bill_report_action.xml',
        'wizard/bank_and_cash_wizard.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
