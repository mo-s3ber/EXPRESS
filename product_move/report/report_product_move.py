from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz

_logger = logging.getLogger(__name__)
from collections import OrderedDict


class ReportPeriodicalSale(models.AbstractModel):
    _name = "report.product_move.report_product_move"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data["form"]["date_from"]
        date_to = data["form"]["date_to"]
        pro = data["form"]["product"]
        analytical_account_id=data["form"]["analytical_account_id"]
        total_sale = 0.0
        period_value = ""
        domain = []
        if analytical_account_id :
            domain.append(('analytic_account_id','=',analytical_account_id))

        stock_moves = self.env["stock.move"].search(domain, order="date,product_id asc")
        ids=[]
        dates=[]
        if date_from:
           date_from=datetime.datetime.strptime(date_from, '%Y-%m-%d')
        if date_to:
            date_to=datetime.datetime.strptime(date_to, '%Y-%m-%d')

        old_timezone = pytz.timezone("UTC")
        new_timezone = pytz.timezone("Africa/Cairo") 
        check_i=False
        if date_from or date_to:
            for rec in stock_moves:
                 
                
                last_new_timezone = old_timezone.localize(rec.date).astimezone(new_timezone)
                last_new_timezone=last_new_timezone.strftime('%Y-%m-%d')
                
                last_new_timezone=datetime.datetime.strptime(last_new_timezone, '%Y-%m-%d')
                if date_to and date_from:

                    if date_from<=last_new_timezone and date_to>=last_new_timezone:
                        ids.append(rec.id)
                elif date_from:
                    if date_from<=last_new_timezone:
                        ids.append(rec.id)
                elif date_to:
                    if date_to>=last_new_timezone :
                        ids.append(rec.id)

            if ids:
                stock_moves=self.env["stock.move"].search([('id','in',ids)],order="product_id,date asc")
            else:
                stock_moves=[]

        moves = []
        order_line = []

        _logger.info("STOKE MOVE")
        note_sale = ""
        note_purchase = ""
        for rec in stock_moves:
            last_new_timezone = old_timezone.localize(rec.date).astimezone(new_timezone)
            last_new_timezone=last_new_timezone.strftime('%Y-%m-%d')
            if rec.state != "cancel":
                if pro:
                    if pro == rec.product_id.id:
                        if rec.picking_id:
                            if rec.picking_id.sale_id:
                                order_line = self.env["sale.order.line"].search(
                                    [("move_ids", "=", rec.id)]
                                )
                                note_sale = order_line.note_sale

                            if rec.picking_id.purchase_id:
                                order_line = self.env["purchase.order.line"].search(
                                    [("move_ids", "=", rec.id)]
                                )
                                note_purchase = order_line.note_purchase
                            moves.append(
                                {
                                    "name": rec.name,
                                    "date": last_new_timezone,
                                    "partner": rec.picking_id.partner_id.name,
                                    "product_id": rec.product_id.name,
                                    "quantity": rec.product_uom_qty,
                                    "so": rec.picking_id.sale_id.name,
                                    "po": rec.picking_id.purchase_id.name,
                                    "sale_id": rec.picking_id.sale_id.id,
                                    "purchase_id": rec.picking_id.purchase_id.id,
                                    "id": rec.product_id.id,
                                    "note_sale": note_sale,
                                    "note_purchase": note_purchase,
                                }
                            )
                        else:
                            moves.append(
                                {
                                    "name": "",
                                    "date": last_new_timezone,
                                    "partner": "رصيد اول المده",
                                    "product_id": rec.product_id.name,
                                    "quantity": rec.product_uom_qty,
                                    "so": "",
                                    "po": "",
                                    "sale_id": 0,
                                    "purchase_id": 0,
                                    "id": rec.product_id.id,
                                    "note_purchase": "",
                                    "note_sale": "",
                                }
                            )
                else:

                    if rec.picking_id:
                        if rec.picking_id.sale_id:
                            order_line = self.env["sale.order.line"].search(
                                [("move_ids", "=", rec.id)]
                            )
                            note_sale = order_line.note_sale
                            _logger.info("ggggggggggggggg")
                            _logger.info(note_sale)
                        if rec.picking_id.purchase_id:
                            order_line = self.env["purchase.order.line"].search(
                                [("move_ids", "=", rec.id)]
                            )
                            note_purchase = order_line.note_purchase
                        moves.append(
                            {
                                "name": rec.name,
                                "date":last_new_timezone,
                                "partner": rec.picking_id.partner_id.name,
                                "product_id": rec.product_id.name,
                                "quantity": rec.product_uom_qty,
                                "so": rec.picking_id.sale_id.name,
                                "po": rec.picking_id.purchase_id.name,
                                "sale_id": rec.picking_id.sale_id.id,
                                "purchase_id": rec.picking_id.purchase_id.id,
                                "id": rec.product_id.id,
                                "note_sale": note_sale,
                                "note_purchase": note_purchase,
                            }
                        )
                    else:
                        moves.append(
                            {
                                "name": "",
                                "date": last_new_timezone,
                                "partner": "رصيد اول المده",
                                "product_id": rec.product_id.name,
                                "quantity": rec.product_uom_qty,
                                "so": "",
                                "po": "",
                                "sale_id": 0,
                                "purchase_id": 0,
                                "id": rec.product_id.id,
                                "note_purchase": "",
                                "note_sale": "",
                            }
                        )
        if date_from:
           date_from=date_from.strftime('%Y-%m-%d')
        if date_to:
           date_to=date_to.strftime('%Y-%m-%d')
        if len(moves) != 0:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "date_from": date_from,
                "date_to": date_to,
                "moves": moves,
                "product_name":self.env['product.product'].search([('id','=',pro)]).name,
                "data_check": False,
                "analytical_account_id":self.env['account.analytic.account'].search([('id','=',analytical_account_id)]).name,
                'name_report':'كارت الصنف'
            }
        else:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "date_from": date_from,
                "date_to": date_to,
                "moves": moves,
                "product_name":self.env['product.product'].search([('id','=',pro)]).name,
                "data_check": True,
                "analytical_account_id":self.env['account.analytic.account'].search([('id','=',analytical_account_id)]).name,
                'name_report':'كارت الصنف'
            }

