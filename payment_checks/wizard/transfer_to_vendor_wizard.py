# -*- coding: utf-8 -*-
# Part of Kanak Infosystems LLP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import UserError


class TransferVendor(models.TransientModel):
    _name = 'transfer.vendor'
    _description = 'Transfer to Vendor'

    check_id = fields.Many2one('payment.check', 'Check')
    partner_id = fields.Many2one('res.partner', 'Vendor')

    def action_post(self):
        self.ensure_one()
        vals = []
        vals.append(self.check_id._prep_credit_val(self.check_id.number,self.check_id.amount,self.check_id.journal_id.holding_check_account_id,self.partner_id,self.check_id.currency_id))
        vals.append(self.check_id._prep_debit_val(self.check_id.number,self.check_id.amount,self.partner_id.property_account_payable_id,self.partner_id,self.check_id.currency_id))
        self.check_id._create_entry(self.check_id.journal_id,fields.Date.today(),vals)
        self.check_id.state ='transfer'
        return {'type': 'ir.actions.act_window_close'}
