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


class PartnerStatement(models.TransientModel):
    _name = "partner.statement.t.report"

    date_from = fields.Date(string='تاريخ البدء')
    date_to = fields.Date(string='تاريخ الانتهاء')
    partner_id = fields.Many2one('res.partner',required=1)
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
    def get_all_move(self, partner_id):
        domain = [('account_id', 'in',
                   (partner_id.property_account_receivable_id.id, partner_id.property_account_payable_id.id)),
                  ('partner_id', '=', partner_id.id), ('date', '>=', self.date_from),
                  ('date', '<=', self.date_to), ('company_id', '=', self.env.user.company_id.id)]
        if self.analytical_account_id:
            domain.append(('analytic_account_id', '=', self.analytical_account_id.id))
        if self.state != 'all':
            domain.append(('move_id.state', '=', self.state))
        lines = self.env['account.move.line'].search(domain, order='date')
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
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 8,
            'fg_color': '#E4D8DC',
        })
        title_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'text_wrap': True,
            'font_size': 10,
            'valign': 'vcenter',
            'fg_color': '#93B5C6'
        })

        table_header_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'text_wrap': True,
            'font_size': 10,
            'valign': 'vcenter',
            'fg_color': '#C9CCD5'
        })

        worksheet = workbook.add_worksheet('كشف حساب T')
        worksheet.set_paper(9)
        worksheet.set_portrait()
        worksheet.right_to_left()
        worksheet.set_column('A:W', 15)
        worksheet.set_column('B:B', 25)
        worksheet.merge_range(0, 0, 1, 7, 'كشف حساب عميل T', title_format)
        worksheet.write(2, 0, 'من', table_header_format)
        worksheet.write(2, 1, str(self.date_from), table_header_format)
        worksheet.write(2, 2, 'الي', table_header_format)
        worksheet.write(2, 3, str(self.date_to), table_header_format)
        worksheet.write(2, 4, "مدين", table_header_format)
        worksheet.write(2, 5, "داين", table_header_format)
        worksheet.write(2, 6, "الرصيد", table_header_format)
        row = 3
        for partner in self.get_partner():
            if self.get_all_move(partner):
                worksheet.merge_range(row, 0, row, 3, partner.name, partner_format)
                debit = round(sum([x.debit for x in self.get_all_move(partner).filtered(lambda x: x.debit > 0.0)]), 2)
                credit = round(sum([x.credit for x in self.get_all_move(partner).filtered(lambda x: x.credit > 0.0)]),
                               2)
                worksheet.write(row, 4, debit, partner_format)
                worksheet.write(row, 5, credit, partner_format)
                worksheet.write(row, 6, round(debit - credit, 2), partner_format)
                row += 1
                qty_total = 0.0
                price_total = 0.0
                worksheet.write(row, 0, 'التاريخ', table_header_format)
                worksheet.write(row, 1, 'الاذن', table_header_format)
                worksheet.write(row, 2, 'تاريخ الفاتورة', table_header_format)
                worksheet.write(row, 3, 'الصنف', table_header_format)
                worksheet.write(row, 4, 'الكمية', table_header_format)
                worksheet.write(row, 5, 'قيمة الوحدة', table_header_format)
                worksheet.write(row, 6, 'المبلغ', table_header_format)
                worksheet.write(row, 7, 'ملاحظات', table_header_format)
                row += 1
                col = 0
                for value in self.get_all_move(partner).filtered(lambda x: x.debit > 0.0):
                    if value.invoice_id.invoice_line_ids:
                        for inv in value.invoice_id.invoice_line_ids:
                            qty_total += inv.quantity
                            price_total += inv.price_total
                            worksheet.write(row, col, str(value.date), custom_format)
                            worksheet.write(row, col + 1, str(inv.invoice_id.origin),
                                            custom_format)
                            worksheet.write(row, col + 2, str(inv.invoice_id.date_invoice), custom_format)
                            worksheet.write(row, col + 3, str(inv.product_id.name or ''), custom_format)
                            worksheet.write(row, col + 4, round(inv.quantity, 2), custom_format)
                            worksheet.write(row, col + 5, round(inv.price_unit, 2), custom_format)
                            worksheet.write(row, col + 6, round(inv.price_total, 2), custom_format)
                            worksheet.write(row, col + 7, str(inv.note_invoice or ''), custom_format)
                            row += 1
                    else:
                        qty_total += 1
                        price_total += value.debit
                        worksheet.write(row, col, str(value.date), custom_format)
                        worksheet.write(row, col + 1, str(value.move_id.name or '') + '-' + str(value.name or ''),
                                        custom_format)
                        worksheet.write(row, col + 2, str(value.date), custom_format)
                        worksheet.write(row, col + 3, str(value.name or ''), custom_format)
                        worksheet.write(row, col + 4, round(1, 2), custom_format)
                        worksheet.write(row, col + 5, round(value.debit, 2), custom_format)
                        worksheet.write(row, col + 6, round(value.debit, 2), custom_format)
                        worksheet.write(row, col + 7, '', custom_format)
                        row += 1
                worksheet.write(row, col, '', table_header_format)
                worksheet.write(row, col + 1, '', table_header_format)
                worksheet.write(row, col + 2, '', table_header_format)
                worksheet.write(row, col + 3, '', table_header_format)
                worksheet.write(row, col + 4, round(qty_total, 2), table_header_format)
                worksheet.write(row, col + 5, '', table_header_format)
                worksheet.write(row, col + 6, round(price_total, 2), table_header_format)
                worksheet.write(row, col + 7, '', table_header_format)
                row += 1
                total_credit = 0.0
                row = 4
                worksheet.write(row, 9, 'التاريخ', table_header_format)
                worksheet.write(row, 10, 'البيان', table_header_format)
                worksheet.write(row, 11, 'المبلغ', table_header_format)
                row += 1
                col = 9
                for value in self.get_all_move(partner).filtered(lambda x: x.credit > 0.0):
                    total_credit += value.credit
                    worksheet.write(row, col, str(value.date), custom_format)
                    worksheet.write(row, col + 1, str(value.move_id.name or '') + '-' + str(value.name or ''),
                                    custom_format)
                    worksheet.write(row, col + 2, round(value.credit, 2), custom_format)
                    row += 1
                worksheet.write(row, col, '', table_header_format)
                worksheet.write(row, col + 1, '', table_header_format)
                worksheet.write(row, col + 2, round(total_credit, 2), table_header_format)
                row += 1
            else:
                raise ValidationError(_("Nothing to Print!"))

        workbook.close()
        output.seek(0)
        self.write({'excel_sheet': base64.encodestring(output.getvalue())})

        return {
            'type': 'ir.actions.act_url',
            'name': 'partner.statement.t.report',
            'url': '/web/content/partner.statement.t.report/%s/excel_sheet/Report.xlsx?download=true' % (
                self.id),
            'target': 'self'
        }
