from odoo import api, models,fields
from dateutil.relativedelta import relativedelta
import datetime
import logging
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError,UserError
from datetime import *
_logger = logging.getLogger(__name__)
class account(models.Model):
    _inherit='account.payment'
    analytical_account=fields.Many2one("account.analytic.account",String="الحساب التحليلي ")
    @api.constrains("state")
    def get_state(self):
        if self.state=='posted' and self.partner_id:
            move_line=self.env['account.move.line'].search([('payment_id','=',self.id)])
            for rec in move_line:
                if self.partner_id.property_account_receivable_id.id==rec.account_id.id or self.partner_id.property_account_payable_id.id==rec.account_id.id:
                           rec.analytic_account_id=self.analytical_account.id
