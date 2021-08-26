# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError
from odoo.addons import decimal_precision as dp
from datetime import date, datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    business_type = fields.Char('Business')
    is_contracting_bill = fields.Boolean()
    date_to = fields.Date('Date to')
    analytic_id = fields.Many2one('account.analytic.account', string='Project')
    business_state = fields.Selection([("run", "In Running"), ("finish", "Finished")], 'Business Status')
    partner_id = fields.Many2one('res.partner', compute='_compute_partner_id', inverse="_set_partner_id",
                                 string="Partner", store=True, readonly=False)

    def _set_partner_id(self):
        if self.partner_id != False:
            return True

    @api.constrains('date', 'date_to')
    def _validate_date(self):
        for rec in self:
            if rec.date and rec.date_to:
                if rec.date_to < rec.date:
                    raise ValidationError(_('"Date To" time cannot be earlier than "Date From" time.'))


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    current_qty = fields.Float(string='Current QTY', digits=dp.get_precision('Product Unit of Measure'))
    previous_qty = fields.Float(string='Previous QTY', digits=dp.get_precision('Product Unit of Measure'))
    percentage = fields.Float('Percentage(%)')
    price_unit = fields.Float(string='Price', digits=dp.get_precision('Product Unit of Measure'))

    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.move_id.partner_id and self.move_id.is_contracting_bill:
            self.partner_id = self.move_id.partner_id.id or self.move_id.partner_id
        if self.move_id.analytic_id and self.move_id.is_contracting_bill:
            self.analytic_account_id = self.move_id.analytic_id.id or self.move_id.analytic_id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id and self.move_id.is_contracting_bill:
            self.name = self.product_id.name
            self.price_unit = self.product_id.price_compute('standard_price')[self.product_id.id]
            self.product_uom_id = self.product_id.uom_id

    @api.onchange('current_qty', 'previous_qty')
    def onchange_qty(self):
        if self.move_id.is_contracting_bill:
            self.quantity = self.current_qty + self.previous_qty

    @api.onchange('quantity', 'percentage', 'price_unit')
    def onchange_amount(self):
        if self.move_id.is_contracting_bill and self.quantity > 0.0 and self.percentage > 0.0 and self.price_unit > 0.0:
            self.debit = self.quantity * (self.percentage / 100) * self.price_unit
            self.credit = 0.0

    @api.constrains('percentage')
    def _validate_percentage(self):
        for rec in self:
            if rec.percentage > 0.0:
                if rec.percentage > 100.0:
                    raise ValidationError(_('Percentage(%) cannot be bigger than 100(%).'))
