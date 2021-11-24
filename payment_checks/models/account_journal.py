from odoo import fields, api, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    checkbook_ids = fields.One2many('check.book','journal_id')
    is_check = fields.Boolean()
    holding_check_account_id = fields.Many2one('account.account', string='Check Holding Account')
    deposited_check_account_id = fields.Many2one('account.account', string='Check Deposited Account')
    debited_check_account_id = fields.Many2one('account.account', string='Check Debited Account')

    handed_check_account_id = fields.Many2one('account.account', string='Check Handed Account')
    credited_check_account_id = fields.Many2one('account.account', string='Check Credited Account')
    check_type = fields.Selection(
        [
            ('receive', 'Receive'),
            ('issue', 'Issue'),
        ], string='Check Type')

