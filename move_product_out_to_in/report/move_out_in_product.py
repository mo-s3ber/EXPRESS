################################################################################ -*- coding: utf-8 -*-

###############################################################################
#
#    Periodical Sales Report
#
#    Copyright (C) 2019 Aminia Technology
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz

_logger = logging.getLogger(__name__)


class ReportProductmoveoutin(models.AbstractModel):
    _name = "report.move_product_out_to_in.report_move_out_in_product"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data["form"]["date_from"]
        date_to = data["form"]["date_to"]
        pro = data["form"]["product"]
        customer = data["form"]["customer"]
        vendor = data["form"]["vendor"]

        total_sale = 0.0
        period_value = ""
        domain = []
        domain_purchase = []

        

        if customer:
            domain.append(("partner_id", "=", customer))
        if vendor:
            domain_purchase.append(("partner_id", "=", vendor))

        sale_orders = []
        purchase_orders = []
        order_line = []
        purchases = self.env["purchase.order"].search(domain_purchase,order="date_order asc")
        ids=[]
        dates=[]
        if date_from:
           date_from=datetime.datetime.strptime(date_from, '%Y-%m-%d')
        if date_to:
            date_to=datetime.datetime.strptime(date_to, '%Y-%m-%d')

        old_timezone = pytz.timezone("UTC")
        new_timezone = pytz.timezone("Africa/Cairo") 
        if date_from or date_to:
            for rec in purchases:
                last_new_timezone = old_timezone.localize(rec.date_order).astimezone(new_timezone)
                last_new_timezone=last_new_timezone.strftime('%Y-%m-%d')
                last_new_timezone=datetime.datetime.strptime(last_new_timezone, '%Y-%m-%d')
                _logger.info("last_new_timezone")
                
                
               
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
               purchases=self.env["purchase.order"].search([('id','in',ids)],order="date_order asc")
            else:
                purchases=[]

        for rec in purchases:
            total_sale = 0
            count_invoice = 0
            s_order_line_list=[]
            if rec.state != "cancel":
                count_invoice = len(rec.invoice_ids)
                
                for order in rec.order_line:
                    check_dup=True
                    s_order_line=self.env['purchase.order.line'].search([('order_id','=',rec.id),('product_id','=',order.product_id.id)])
                 
                    for lst in s_order_line:
                     

                      if lst.product_id.id not in s_order_line_list:
                           check_dup=False
                       
                           s_order_line_list.append(lst.product_id.id)
                    _logger.info("partner")
                    _logger.info(order.order_id.partner_id.company_id)

                    if pro:
                        if pro == order.product_id.id:
                            purchase_orders.append(
                                {
                                    "name": rec.name,
                                    "product_id": order.product_id.name,
                                    "date_one": rec.date_order,
                                    "partner": order.order_id.partner_id.name,
                                    "amount_total": order.price_total,
                                    "order_id": order.order_id.name,
                                    "quantity": order.product_qty,
                                    "price_unit": order.price_unit,
                                    "count_invoice": count_invoice,
                                    "total": order.price_total,
                                    "pro_id": order.product_id,
                                    "category": order.product_id.categ_id,
                                    "id": order.product_id.id,
                                    "check_dup":check_dup
                                }
                            )
                    else:
                        purchase_orders.append(
                            {
                                "name": rec.name,
                                "product_id": order.product_id.name,
                                "date_one": rec.date_order,
                                "partner": order.order_id.partner_id.name,
                                "amount_total": order.price_total,
                                "order_id": order.order_id.name,
                                "quantity": order.product_qty,
                                "price_unit": order.price_unit,
                                "count_invoice": count_invoice,
                                "total": order.price_total,
                                "pro_id": order.product_id,
                                "category": order.product_id.categ_id,
                                "id": order.product_id.id,
                                "check_dup":check_dup
                            }
                        )

        orders = self.env["sale.order"].search(domain,order="date_order asc")
        ids=[]
        if date_from or date_to:
            for rec in orders:
                last_new_timezone = old_timezone.localize(rec.date_order).astimezone(new_timezone)
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
               orders=self.env["sale.order"].search([('id','in',ids)],order="date_order asc")
            else:
                orders=[]
        for rec in orders:
            total_sale = 0
            count_invoice = 0
            s_order_line_list=[]
            if rec.state != "cancel":
                # if   rec.picking_ids.date_done:
                count_invoice = len(rec.invoice_ids)
                for order in rec.order_line:
                    _logger.info(type(order.product_id.id))
                    _logger.info(pro)
                    check_dup=True
                    s_order_line=self.env['sale.order.line'].search([('order_id','=',rec.id),('product_id','=',order.product_id.id)])
                    
                    for lst in s_order_line:
                         
                           

                        if lst.product_id.id not in s_order_line_list:
                           check_dup=False
                           s_order_line_list.append(lst.product_id.id)

                    if pro:
                        if pro == order.product_id.id:
                            sale_orders.append(
                                {
                                    "name": rec.name,
                                    "product_id": order.product_id.name,
                                    "date_one": rec.date_order,
                                    "partner": order.order_id.partner_id.name,
                                    "amount_total": order.price_total,
                                    "order_id": order.order_id.name,
                                    "quantity": order.product_uom_qty,
                                    "price_unit": order.price_unit,
                                    "count_invoice": count_invoice,
                                    "total": order.price_total,
                                    "pro_id": order.product_id,
                                    "category": order.product_id.categ_id,
                                    "id": order.product_id.id,
                                    "check_dup":check_dup

                                }
                            )
                    else:
                        sale_orders.append(
                            {
                                "name": rec.name,
                                "product_id": order.product_id.name,
                                "date_one": rec.date_order,
                                "partner": order.order_id.partner_id.name,
                                "amount_total": order.price_total,
                                "order_id": order.order_id.name,
                                "quantity": order.product_uom_qty,
                                "price_unit": order.price_unit,
                                "count_invoice": count_invoice,
                                "total": order.price_total,
                                "pro_id": order.product_id,
                                "category": order.product_id.categ_id,
                                "id": order.product_id.id,
                                "check_dup":check_dup
                            }
                        )
        if len(sale_orders) != 0:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "date_to": date_to,
                "purchase_orders": purchase_orders,
                "sale_orders": sale_orders,
                "total_sale": total_sale,
                "customer_name": self.env["res.partner"].search([("id", "=", customer)]).name,
                "vendor_name": self.env["res.partner"].search([("id", "=", vendor)]).name,
                "product_name": self.env["product.product"].search([("id", "=", pro)]).name,
                "data_check": False,
                'name_report':'بيان حركه صنف لعميل مقابل الموردين'
            }
        else:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "date_to": date_to,
                "purchase_orders": purchase_orders,
                "sale_orders": sale_orders,
                "total_sale": total_sale,
                "customer_name": self.env["res.partner"].search([("id", "=", customer)]).name,
                "vendor_name": self.env["res.partner"].search([("id", "=", vendor)]).name,
                "product_name": self.env["product.product"].search([("id", "=", pro)]).name,
                "data_check": True,
                'name_report':'بيان حركه صنف لعميل مقابل الموردين'
            }

