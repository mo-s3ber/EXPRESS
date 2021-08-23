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
    'name': "Express Invoice Print",

    'summary': """
    Express Invoice Print
        """,

    'description': """
   Express Invoice Print
    """,

    'author': "Mohamed Saber",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': "12.0.0.1",

    # any module necessary for this one to work correctly
    'depends': ['base','mail','account','account_accountant','company_extented_fields'],

    # always loaded
    'data': [
        'views/res_currency.xml',
        'report/express_invoice_report_view.xml',
        'report/invoice_report_action.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
