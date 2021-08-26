# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError
from odoo.exceptions import ValidationError
import base64
import xlsxwriter
import io
from datetime import datetime, time, timedelta
from dateutil.rrule import rrule, DAILY
from functools import partial
from itertools import chain
from pytz import timezone, utc
from datetime import datetime
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import date
import datetime


def is_int(n):
    try:
        float_n = float(n)
        int_n = int(float_n)
    except ValueError:
        return False
    else:
        return float_n == int_n


def is_float(n):
    try:
        float_n = float(n)
    except ValueError:
        return False
    else:
        return True


class PartnerLedger(models.TransientModel):
    _name = "partner.ledger.report"

    date_from = fields.Date(string='تاريخ البدء')
    date_to = fields.Date(string='تاريخ الانتهاء')
    partner_id = fields.Many2one('res.partner')
    analytical_account_id = fields.Many2one('account.analytic.account', string="الحساب التحليلي")
    type = fields.Selection([('customer','عميل'),('vendor','مورد')])
    state = fields.Selection([('draft', 'غير مرحل'), ('posted', 'مرحل'),('all', 'الكل')],string='الحالة' ,default='posted')
    excel_sheet = fields.Binary('Download Report')

    @api.constrains('date_from', 'date_to')
    def _validate_date(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_to < rec.date_from:
                    raise ValidationError(_('"Date To" time cannot be earlier than "Date From" time.'))


    def get_partner(self):
        if self.type == 'customer':
            if self.partner_id:
                partners = [self.partner_id]
            else:
                partners = self.env['res.partner'].search([('customer', '=', True)],order='name')
        else:
            if self.partner_id:
                partners = [self.partner_id]
            else:
                partners = self.env['res.partner'].search([('supplier', '=', True)],order='name')
        return partners

    @api.multi
    def get_all_move(self,partner):
        domain = [('account_id', 'in', (partner.property_account_receivable_id.id,partner.property_account_payable_id.id)),
                  ('partner_id', '=', partner.id), ('date', '>=', self.date_from),
                  ('date', '<=', self.date_to),
                  ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                  ('amount_residual_currency', '!=', 0.0)]
        if self.analytical_account_id:
            domain.append(('analytic_account_id', '=', self.analytical_account_id.id))
        if self.state != 'all':
            domain.append(('move_id.state', '=', self.state))
        lines = self.env['account.move.line'].search(domain,order='date')
        return lines

    @api.multi
    def generate_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        custom_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 8,
            'fg_color': 'white',
        })
        partner_format = workbook.add_format({
            'bold': 1,
            'border': 0,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 8,
            'fg_color': 'F0E5CF',
        })

        table_header_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'center',
            'text_wrap': True,
            'font_size': 10,
            'valign': 'vcenter',
            'fg_color': '#d8d6d6'
        })

        worksheet = workbook.add_worksheet('كشف حساب')
        worksheet.set_paper(9)
        worksheet.set_portrait()
        worksheet.set_column('A:W', 15)
        worksheet.set_column('B:B', 25)
        worksheet.merge_range(0, 0, 1, 4, 'كشف حساب', table_header_format)
        if self.date_from and self.date_to:
            worksheet.write(2, 0, str('مورد' if self.type == 'vendor' else 'عميل'), table_header_format)
            worksheet.write(2, 1, 'من', table_header_format)
            worksheet.write(2, 2, str(self.date_from), table_header_format)
            worksheet.write(2, 3, 'الي', table_header_format)
            worksheet.write(2, 4, str(self.date_to), table_header_format)
        row = 3
        worksheet.write(row, 0, 'التاريخ', table_header_format)
        worksheet.write(row, 1, 'الاذن', table_header_format)
        worksheet.write(row, 2, 'أسم الحساب', table_header_format)
        worksheet.write(row, 3, 'مدين', table_header_format)
        worksheet.write(row, 4, 'داين', table_header_format)
        worksheet.write(row, 5, 'الرصيد', table_header_format)
        row += 1
        for partner in self.get_partner():
            if self.get_all_move(partner):
                col = 0
                debit = 0.0
                credit = 0.0
                balance = 0.0
                worksheet.write(row, 0, str(''), partner_format)
                worksheet.write(row, 1, str(partner.name), partner_format)
                worksheet.write(row, 2, str(''), partner_format)
                worksheet.write(row, 3, str(''), partner_format)
                worksheet.write(row, 4, str(''), partner_format)
                worksheet.write(row, 5, str(''), partner_format)
                row += 1
                for value in self.get_all_move(partner):
                    worksheet.write(row, col, str(value.date), custom_format)
                    worksheet.write(row, col + 1, str(value.move_id.name or '') + '-' + str(value.name or ''),
                                    custom_format)
                    worksheet.write(row, col + 2, str(value.account_id.name), custom_format)
                    worksheet.write(row, col + 3, round(value.debit, 2), custom_format)
                    debit += round(value.debit, 2)
                    worksheet.write(row, col + 4, round(value.credit, 2), custom_format)
                    credit += round(value.credit, 2)
                    balance += round(value.debit, 2) - round(value.credit, 2)
                    worksheet.write(row, col + 5,round(value.debit, 2) - round(value.credit, 2), custom_format)
                    row += 1
                worksheet.write(row, col + 2, 'الاجمالي', custom_format)
                worksheet.write(row, col + 3, debit, custom_format)
                worksheet.write(row, col + 4, credit, custom_format)
                worksheet.write(row, col + 5, balance, custom_format)
                row += 1

        workbook.close()
        output.seek(0)
        self.write({'excel_sheet': base64.encodestring(output.getvalue())})

        return {
            'type': 'ir.actions.act_url',
            'name': 'partner.ledger.report',
            'url': '/web/content/partner.ledger.report/%s/excel_sheet/Report.xlsx?download=true' % (
                self.id),
            'target': 'self'
        }



