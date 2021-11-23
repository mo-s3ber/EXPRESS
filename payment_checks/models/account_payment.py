from odoo import fields, api, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    checks_ids = fields.One2many('payment.check','payment_id')