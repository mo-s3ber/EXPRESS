from odoo import fields, api, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    checkbook_ids = fields.One2many('check.book','journal_id')
