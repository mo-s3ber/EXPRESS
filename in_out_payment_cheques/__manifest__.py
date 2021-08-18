 
{
    'name' : 'in out payment cheques T',
    'version' : '12.0.1',
    'summary': 'Module customer Statment T .',
    'sequence': 16,
    'category': 'Account',
    'author' : 'BBl',
    'description': """
Custom Sales Report
=====================================
This module print daily, last week and last month sale report.
Also print report for particular duration.
    """,
    "license": "AGPL-3",
    'depends' : ['base_setup', 'sale_management','account','move_product_in_to_out'],
    'data': [
        'wizard/wiz_cuatomer_statement_view.xml',
        'views/customer_statement_view.xml',
        'views/report_customer_statment.xml'
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
