from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError,UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import datetime as dt
from datetime import datetime, timedelta
import calendar
import time
import re
from odoo.addons import decimal_precision as dp
from dateutil import relativedelta
import logging
_logger = logging.getLogger(__name__)
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
class Invoice(models.Model):
    _inherit ='account.invoice'

    def action_invoice_open(self):
        res = super(Invoice, self).action_invoice_open()
        anyltical_account = ''
        print(">>>>>>>>>>>>>.", self.move_id)

        if self.move_id:
            for rec in self.invoice_line_ids:
                if rec.account_analytic_id:
                    anyltical_account = rec.account_analytic_id
        for move in self.move_id.line_ids:
            if not move.analytic_account_id and anyltical_account and move.account_id == move.partner_id.property_account_receivable_id:
                move.analytic_account_id = anyltical_account.id
        return res
class sale_custom(models.Model):
    _inherit="account.invoice.line"
    note_invoice=fields.Char('ملاحظات',compute='_get_note')


    @api.one
    @api.depends('sale_line_ids','purchase_line_id')
    def _get_note(self):
        _logger.info('Note Of invoice Line')
        for rec in self.sale_line_ids:
            self.note_invoice=rec.note_sale
        if self.purchase_line_id:
            self.note_invoice=self.purchase_line_id.note_purchase


        _logger.info(self.note_invoice)

 
class account_move(models.Model):
      _inherit='account.move'
      begin_balance=fields.Boolean('رصيد افتتاحي')
      Customer=fields.Boolean(related='partner_id.customer',string="customer")

