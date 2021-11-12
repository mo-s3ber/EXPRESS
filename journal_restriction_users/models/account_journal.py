
from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError

class Users(models.Model):

    _inherit = 'res.users'

    journal_ids = fields.Many2many(
        'account.journal',
        'journal_security_journal_users',
        'user_id',
        'journal_id',
        'Restricted Journals (TOTAL)'
    )


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    user_ids = fields.Many2many('res.users','journal_security_journal_users',
                                'journal_id','user_id',string='Allowed Users',
                                help='If choose some users, then this journal and the information'
                                ' related to it will be only visible for those users.',
                                    copy=False,
                                )