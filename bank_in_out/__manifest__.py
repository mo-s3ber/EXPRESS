
{
    'name' : 'Bank IN OUT ',
    'version' : '12.0.1',
    'summary': 'Module all Cheques of Bank .',
    'sequence': 16,
    'category': 'Account',
    'author' : 'BBl',
    'description': """
    """,
    "license": "AGPL-3",
    'depends' : ['base_setup', 'sale_management','account','move_product_in_to_out'],
    'data': [
        'wizard/wiz_bank_cheques_view.xml',
        'views/bank_cheques_view.xml',
        'views/report_bank_cheques.xml'
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
