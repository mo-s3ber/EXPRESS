# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import time
from datetime import date
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree
# from datetime import datetime, date
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

from odoo.osv import expression


class PaymentCheck(models.Model):
    _name = 'payment.check'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Account Check Payment"
    _order = 'date desc'

    name = fields.Char(string='Name', size=64, readonly=True, default='/', copy=False)
    number = fields.Char(string='Number', size=64)
    journal_id = fields.Many2one(
        'account.journal', string='Journal',
        domain=[('type', '=', 'bank')],
        required=True)
    checkbook_id = fields.Many2one('check.book',required=True)
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',string="Currency")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    date = fields.Date(
        string='Date', required=True,
        default=fields.Date.context_today)
    type = fields.Selection(
        [
            ('issue', 'Issue'),
            ('third', 'Third'),
        ], string='Status', default='draft', readonly=True)
    payment_id = fields.Many2one('account.payment')
    partner_id = fields.Many2one(related='payment_id.partner_id', store=True)
    payment_date = fields.Date(related='payment_id.date', store=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('handed', 'Handed'),
            ('holding', 'Holding'),
            ('debited', 'Debited'),
            ('deposited', 'Deposited'),
            ('rejected', 'Rejected'),
            ('returned', 'Returned'),
            ('changed', 'changed'),
            ('canceled', 'Canceled')
        ], string='Status', default='draft', readonly=True)

    @api.onchange('payment_id')
    def onchange_payment_id(self):
        for rec in self:
            if rec.payment_id.payment_type == 'inbound':
                rec.type = 'third'
            if rec.payment_id.payment_type == 'outbound':
                rec.type = 'issue'




    def button_draft(self):
        return self.write({"state": "draft"})

    def button_handed(self):
        return self.write({"state": "handed"})

    def button_holding(self):
        return self.write({"state": "holding"})

    def button_debited(self):
        return self.write({"state": "debited"})

    def button_deposited(self):
        return self.write({"state": "deposited"})

    def button_rejected(self):
        return self.write({"state": "rejected"})

    def button_returned(self):
        return self.write({"state": "returned"})


    def button_changed(self):
        return self.write({"state": "changed"})

    def button_canceled(self):
        return self.write({"state": "canceled"})

