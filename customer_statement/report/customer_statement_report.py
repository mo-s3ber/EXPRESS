#############################################################################

from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz
_logger = logging.getLogger(__name__)


class ReportProductSale(models.AbstractModel):
    _name = "report.customer_statement.customer_statement_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data["form"]["date_from"]
        date_to = data["form"]["date_to"]
        customer = data["form"]["customer"]
        analytical_account_id = self.env['account.analytic.account'].search([('id','=',data["form"]["analytical_account_id"])])

        total_sale = 0.0
        domain = [("type", "=", "out_invoice"),("state", "not in", ("draft","cancel"))]
        if date_from:
            domain.append(("date_invoice", ">=", date_from))
        if date_to:
            domain.append(("date_invoice", "<=", date_to))
        if customer:
            domain.append(("partner_id", "=", customer))

        orders = []
        invoice_ids = self.env["account.invoice"].search(domain,order='date_invoice asc')
        for inv in invoice_ids:
            sale_order = self.env["sale.order"].search([("name", "=", inv.origin)])
            invoice_line_ids = inv.invoice_line_ids.filtered(lambda x: x.account_analytic_id == analytical_account_id) if analytical_account_id else inv.invoice_line_ids
            for line in invoice_line_ids:
                orders.append(
                    {
                        "so_number": inv.origin,
                        "date_so": sale_order.date_order if sale_order else '',
                        "invoice_number": inv.number,
                        "product_id": line.product_id.name,
                        "inv_name": inv.name,
                        "date_in": inv.date_invoice,
                        "partner": inv.partner_id.name,
                        "quantity": line.quantity,
                        "price_unit": line.price_unit,
                        "total": line.price_total,
                        "note_invoice": line.note_invoice,
                    }
                )
        return {
            "doc_ids": data["ids"],
            "doc_model": data["model"],
            "date_from": date_from,
            "date_to": date_to,
            "sale_orders": orders,
            "customer_name": self.env["res.partner"].search([("id", "=", customer)]).name,
            "analytical_account_id":analytical_account_id.name,
            "name_report":'كشــف فواتير عميل'
        }

