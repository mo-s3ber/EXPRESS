from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz

_logger = logging.getLogger(__name__)


class ReportProductSale(models.AbstractModel):
    _name = 'report.express_partner_statement.vendor_statement_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        vendor = data['form']['vendor']
        analytical_account_id = data['form']['analytical_account_id']
        domain = [('invoice_id.type', '=', 'in_invoice'), ("invoice_id.state", "not in", ("draft", "cancel"))]
        if date_from:
            domain.append(('invoice_id.date_invoice', '>=', date_from))
        if date_to:
            domain.append(('invoice_id.date_invoice', '<=', date_to))
        if vendor:
            domain.append(('partner_id', '=', vendor))
        if analytical_account_id:
            domain.append(('account_analytic_id', '=', analytical_account_id))
        list = []
        invoice_lines_ids = self.env['account.invoice.line'].search(domain, order='id desc')
        for line in invoice_lines_ids:
            list.append({
                'so_number': line.purchase_id.name if line.purchase_id else '',
                'date_so': line.purchase_id.date_order,
                'invoice_number': line.invoice_id.number,
                'product_id': line.product_id.name,
                'inv_name': line.invoice_id.name,
                'date_in': line.invoice_id.date_invoice,
                'partner': line.invoice_id.partner_id.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'total': line.price_total,
                'note_invoice': line.name,

            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': date_from,
            'date_to': date_to,
            'orders': list,
            'vendor_name': self.env['res.partner'].search([('id', '=', vendor)]).name,
            "analytical_account_id": self.env['account.analytic.account'].search(
                [('id', '=', analytical_account_id)]).name,
            "name_report": 'كشــف فواتير مــــــورد'
        }
