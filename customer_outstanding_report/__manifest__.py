# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Archer Solutions
#    Copyright (C) 2019 dev:Mohamed Saber.
#################################################################################

{
    'name': "Customer Outstanding Report",
    'author': 'Archer Solutions',
    'category': 'account_invoicing',
    'summary': """Report for customer's outstanding invoice amount within the particular date period""",
    'website': 'http://www.archersolutions.com',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '12.0.0.1',
    'depends': ['base', 'account'],
    'data': ['wizard/invoice_outstanding.xml', 'views/invoice_outstanding_report_view.xml',
             'report/invoice_outstanding_template.xml', 'report/invoice_outstanding_report.xml'],
    'installable': True,
    'images': ['static/description/banner.png'],
    'application': True,
    'auto_install': False,
}
