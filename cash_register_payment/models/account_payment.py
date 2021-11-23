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


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.constrains('date')
    def constrains_date(self):
        for rec in self:
            bank_statement_id = self.env['account.bank.statement'].search([('date', '=', rec.date),
                                                                           ('id', '!=', rec.id),
                                                                           ('state', '=', 'open'),
                                                                           ('journal_id', '=', rec.journal_id.id),
                                                                           ], limit=1)
            if bank_statement_id:
                raise ValidationError(
                    _('there is an other statement [ %s ] At %s') % (bank_statement_id.name, rec.date))

    def action_re_open(self):
        for rec in self:
            rec.write({'state': 'open'})


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    to_journal_id = fields.Many2one('account.journal', string='Journal to')
    to_move_id = fields.Many2one('account.move', string='Journal Entry to')

    def get_account_statement_from(self):
        statement = self.env['account.bank.statement'].sudo().search(
            [('date', '=', datetime.today()), ('journal_id', '=', self.journal_id.id)], limit=1)
        if statement:
            if statement.state != 'open':
                raise ValidationError(_('"You can not open another statement in Day!"'))
        if not statement:
            statement = self.env['account.bank.statement'].sudo().create(
                {'journal_id': self.journal_id.id, 'date': datetime.today()})
        return statement

    def get_account_statement_to(self):
        statement = self.env['account.bank.statement'].sudo().search(
            [('date', '=', datetime.today()), ('journal_id', '=', self.to_journal_id.id)], limit=1)
        if statement:
            if statement.state != 'open':
                raise ValidationError(_('"You can not open another statement in Day!"'))
        if not statement:
            statement = self.env['account.bank.statement'].sudo().create(
                {'journal_id': self.to_journal_id.id, 'date': datetime.today()})
        return statement

    def create_move_from(self):
        if self.is_internal_transfer:
            destination_account_id = self.to_journal_id.company_id.transfer_account_id
            if self.payment_type == 'inbound':
                # Receive money.
                counterpart_amount = -self.amount
            elif self.payment_type == 'outbound':
                # Send money.
                counterpart_amount = self.amount
            else:
                counterpart_amount = 0.0

            balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id,
                                                self.date)
            counterpart_amount_currency = counterpart_amount
            currency_id = self.currency_id.id
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.to_journal_id.name)
                outstanding_account = self.to_journal_id.payment_credit_account_id.id
            else:  # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer to %s', self.to_journal_id.name)
                outstanding_account = self.to_journal_id.payment_debit_account_id.id

            payment_display_name = {
                'outbound-customer': _("Reimbursement"),
                'inbound-customer': _("Payment"),
                'outbound-supplier': _("Payment"),
                'inbound-supplier': _("Reimbursement"),
            }
            default_line_name = self.env['account.move.line']._get_default_line_name(
                payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
                self.amount,
                self.currency_id,
                self.date,
                partner=self.partner_id,
            )
            vals = [(
                0, 0, {
                    'name': self.payment_reference or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': counterpart_amount_currency if currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': balance < 0.0 and -balance or 0.0,
                    'credit': balance > 0.0 and balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': destination_account_id.id,
                }), (
                0, 0, {
                    'name': liquidity_line_name,
                    'date_maturity': self.date,
                    'amount_currency': counterpart_amount_currency if currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': outstanding_account,
                })]
            move_vals = {
                'journal_id': self.to_journal_id.id,
                'move_type': 'entry',
                'date': self.date,
                'company_id': self.env.user.company_id.id,
                'line_ids': vals,
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            self.write({'to_move_id':move.id})

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for rec in self:
            self.create_move_from()
            statement_from = self.get_account_statement_from()
            self.env['account.bank.statement.line'].sudo().create(
                {'statement_id': statement_from.id, 'date': rec.date, 'payment_ref': rec.name,
                 'partner_id': rec.partner_id.id, 'amount':  rec.amount if rec.payment_type == 'inbound' else -(rec.amount)})
            if rec.is_internal_transfer:
                statement_to = self.get_account_statement_to()
                self.env['account.bank.statement.line'].sudo().create(
                    {'statement_id': statement_to.id, 'date': rec.date, 'payment_ref': rec.name,
                     'partner_id': rec.partner_id.id, 'amount': -(rec.amount) if rec.payment_type == 'inbound' else (rec.amount)})
        return res
