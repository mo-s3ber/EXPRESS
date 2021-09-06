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


class PartnerLedgerTotal(models.TransientModel):
    _name = "partner.ledger.total.report"

    date_from = fields.Date(string='تاريخ البدء')
    date_to = fields.Date(string='تاريخ الانتهاء')
    partner_id = fields.Many2one('res.partner')
    analytical_account_id = fields.Many2one('account.analytic.account', string="الحساب التحليلي")
    type = fields.Selection([('customer', 'عميل'), ('vendor', 'مورد')])
    state = fields.Selection([('draft', 'غير مرحل'), ('posted', 'مرحل'), ('all', 'الكل')], string='الحالة',
                             default='posted')
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
                partners = self.env['res.partner'].search([('customer', '=', True)], order='name')
        else:
            if self.partner_id:
                partners = [self.partner_id]
            else:
                partners = self.env['res.partner'].search([('supplier', '=', True)], order='name')
        return partners

    @api.multi
    def get_all_move(self, partner):
        result = {}
        domain = [
            ('account_id', 'in', (partner.property_account_receivable_id.id, partner.property_account_payable_id.id)),
            ('partner_id', '=', partner.id), ('company_id', '=', self.env.user.company_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to)]
        if self.analytical_account_id:
            domain.append(('analytic_account_id', '=', self.analytical_account_id.id))
        if self.state != 'all':
            domain.append(('move_id.state', '=', self.state))
        lines = self.env['account.move.line'].search(domain, order='date desc')
        for line in lines:
            if line in result.keys():
                result[line.account_id]['debit'] += line.debit
                result[line.account_id]['credit'] += line.credit
            else:
                result[line.account_id] = {'debit': line.debit, 'credit': line.credit}
        return result

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
        worksheet.merge_range(0, 0, 1, 4, 'كشف ارصدة', table_header_format)
        if self.date_from and self.date_to:
            worksheet.write(2, 0, str('مورد' if self.type == 'vendor' else 'عميل'), table_header_format)
            worksheet.write(2, 1, 'من', table_header_format)
            worksheet.write(2, 2, str(self.date_from), table_header_format)
            worksheet.write(2, 3, 'الي', table_header_format)
            worksheet.write(2, 4, str(self.date_to), table_header_format)
        row = 3
        worksheet.write(row, 0, 'أسم الحساب', table_header_format)
        worksheet.write(row, 1, 'مدين', table_header_format)
        worksheet.write(row, 2, 'داين', table_header_format)
        worksheet.write(row, 3, 'الرصيد', table_header_format)
        row += 1
        for partner in self.get_partner():
            if self.get_all_move(partner):
                col = 0
                worksheet.write(row, 0, str(partner.name), partner_format)
                worksheet.write(row, 1, str(''), partner_format)
                worksheet.write(row, 2, str(''), partner_format)
                worksheet.write(row, 3, str(''), partner_format)
                row += 1
                for key,value in self.get_all_move(partner).items():
                    worksheet.write(row, col + 0, str(key.name), custom_format)
                    worksheet.write(row, col + 1, round(value['debit'], 2), custom_format)
                    worksheet.write(row, col + 2, round(value['credit'], 2), custom_format)
                    worksheet.write(row, col + 3, round(value['debit'], 2) - round(value['credit'], 2), custom_format)
                    row += 1

        workbook.close()
        output.seek(0)
        self.write({'excel_sheet': base64.encodestring(output.getvalue())})

        return {
            'type': 'ir.actions.act_url',
            'name': 'partner.ledger.total.report',
            'url': '/web/content/partner.ledger.total.report/%s/excel_sheet/Report.xlsx?download=true' % (
                self.id),
            'target': 'self'
        }
