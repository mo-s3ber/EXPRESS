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

    name = fields.Char(string='Name', size=64, readonly=True,)
    number = fields.Integer(string='Number', size=64, required=1,tracking=True)
    checkbook_id = fields.Many2one('check.book',tracking=True)
    amount = fields.Monetary(currency_field='currency_id',tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    date = fields.Date(
        string='Due Date', required=True,tracking=True)
    type = fields.Selection(
        [
            ('issue', 'Issue'),
            ('receive', 'Receive'),
        ], string='Type')
    payment_id = fields.Many2one('account.payment')
    journal_id = fields.Many2one(
        'account.journal', string='Journal',
        domain=[('type', '=', 'bank')])

    partner_id = fields.Many2one(related='payment_id.partner_id', store=True)
    payment_date = fields.Date(string="Issue Date",tracking=True)
    partner_bank_id = fields.Many2one('res.partner.bank', string='Recipient Bank',
                                      help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Vendor Credit Note, otherwise a Partner bank account number.',
                                      check_company=True,tracking=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('handed', 'Handed'),
            ('holding', 'Holding'),
            ('transfer', 'Transfer'),
            ('deposited', 'Deposited'),
            ('debited', 'Debited'),
            ('credited', 'Credited'),
            ('returned', 'Returned'),
            ('canceled', 'Canceled')
        ], string='Status', default='draft', readonly=True,tracking=True)

    @api.onchange('checkbook_id')
    def onchange_checkbook_id(self):
        for rec in self:
            if rec.checkbook_id:
                rec.number = rec.checkbook_id.number_next_actual

    @api.onchange('payment_id')
    def onchange_payment_id(self):
        self.journal_id = self.payment_id.journal_id.id
        self.payment_date = self.payment_id.date
        self.amount = self.payment_id.amount
        self.currency_id = self.payment_id.currency_id.id
        if self.payment_id.payment_type == 'inbound':
            self.type = 'receive'
        if self.payment_id.payment_type == 'outbound':
            self.type = 'issue'

    def _prep_credit_val(self, ref, credit, account_id, partner_id, currency_id):
        val = (
            0, 0, {
                'name': ref,
                'credit': credit,
                'debit': 0.0,
                'account_id': account_id.id,
                'partner_id': partner_id.id or False,
                'currency_id': currency_id.id or False,
            })
        return val

    def _prep_debit_val(self, ref, debit, account_id, partner_id, currency_id):
        val = (
            0, 0, {
                'name': ref,
                'credit': 0.0,
                'debit': debit,
                'account_id': account_id.id,
                'partner_id': partner_id.id or False,
                'currency_id': currency_id.id or False,
            })
        return val

    def _create_entry(self, journal_id, date, vals):
        move_vals = {
            'journal_id': journal_id.id,
            'move_type': 'entry',
            'date': date,
            'check_id': self.id,
            'company_id': self.company_id.id,
            'line_ids': vals,
        }
        move = self.env['account.move'].create(move_vals)
        move.action_post()

    def move_tree_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Entries',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('check_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def button_draft(self):
        return self.write({"state": "draft"})

    def button_handed(self):
        return self.write({"state": "handed"})

    def button_holding(self):
        return self.write({"state": "holding"})

    def button_deposited(self):
        self.ensure_one()
        vals = []
        vals.append(
            self._prep_credit_val(self.number, self.amount, self.journal_id.holding_check_account_id, self.partner_id,
                                  self.currency_id))
        vals.append(
            self._prep_debit_val(self.number, self.amount, self.journal_id.deposited_check_account_id, self.partner_id,
                                 self.currency_id))
        self._create_entry(self.journal_id, fields.Date.today(), vals)
        return self.write({"state": "deposited"})

    def button_debited(self):
        self.ensure_one()
        vals = []
        vals.append(
            self._prep_credit_val(self.number, self.amount, self.journal_id.deposited_check_account_id, self.partner_id,
                                  self.currency_id))
        vals.append(
            self._prep_debit_val(self.number, self.amount, self.journal_id.debited_check_account_id, self.partner_id,
                                 self.currency_id))
        self._create_entry(self.journal_id, fields.Date.today(), vals)
        return self.write({"state": "debited"})

    def button_credited(self):
        self.ensure_one()
        vals = []
        vals.append(
            self._prep_credit_val(self.number, self.amount, self.journal_id.credited_check_account_id, self.partner_id,
                                  self.currency_id))
        vals.append(
            self._prep_debit_val(self.number, self.amount, self.journal_id.handed_check_account_id, self.partner_id,
                                 self.currency_id))
        self._create_entry(self.journal_id, fields.Date.today(), vals)
        return self.write({"state": "credited"})

    def button_returned(self):
        self.ensure_one()
        vals = []
        if self.state == 'deposited':
            vals.append(self._prep_credit_val(self.number, self.amount, self.journal_id.deposited_check_account_id,
                                              self.partner_id, self.currency_id))
            vals.append(self._prep_debit_val(self.number, self.amount, self.journal_id.holding_check_account_id,
                                             self.partner_id, self.currency_id))
        if self.state == 'holding':
            vals.append(self._prep_credit_val(self.number, self.amount, self.journal_id.holding_check_account_id,
                                              self.partner_id, self.currency_id))
            vals.append(self._prep_debit_val(self.number, self.amount, self.partner_id.property_account_receivable_id,
                                             self.partner_id, self.currency_id))
        self._create_entry(self.journal_id, fields.Date.today(), vals)
        return self.write({"state": "returned"})

    def button_canceled(self):
        self.ensure_one()
        if self.state == 'holding':
            self.payment_id.action_draft()
            self.payment_id.action_cancel()
        if self.state == 'deposited':
            moves = self.env['account.move'].search([('check_id', '=', self.id)])
            for mv in moves:
                mv.button_draft()
                mv.button_cancel()
            self.payment_id.action_draft()
            self.payment_id.action_cancel()
        if self.state == 'handed':
            self.payment_id.action_draft()
            self.payment_id.action_cancel()
        return self.write({"state": "canceled"})

    @api.model
    def create(self, vals):
        vals['name'] = str(vals.get('number')) or '/'
        if vals.get('type') == 'issue':
            checkbook_id = self.env['check.book'].browse(vals.get('checkbook_id'))
            if checkbook_id:
                checkbook_id.number_next_actual = vals.get('number') + 1
        return super(PaymentCheck, self).create(vals)
