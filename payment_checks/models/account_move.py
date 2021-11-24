from odoo import fields, api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    check_id = fields.Many2one('payment.check')
