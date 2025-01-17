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

class ReportPeriodicalSale(models.AbstractModel):
    _name = 'report.total_size_sales.report_total_size_sales'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        customer=data['form']['customer'] 
        analytical_account_id=data['form']['analytical_account_id'] 
        total_sale = 0.0
        period_value = ''
        domain=[]
         
        
        if customer:
            domain.append(('partner_id','=',customer))


         
        sale_orders = []
        order_line=[]
        orders = self.env['sale.order'].search(domain)
        ids=[]
        dates=[]
        if date_from:
           date_from=datetime.datetime.strptime(date_from, '%Y-%m-%d')
        if date_to:
            date_to=datetime.datetime.strptime(date_to, '%Y-%m-%d')

        old_timezone = pytz.timezone("UTC")
        new_timezone = pytz.timezone("Africa/Cairo") 
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
                orders=self.env["sale.order"].search([('id','in',ids)])
            else:
                orders=[]
        invoice_ids_list=[]
        for rec in orders:
            
            total_sale=0
            count_invoice=0
            quantity=0
            total_price=0
            
            if rec.state!='cancel':
                
                for lst in rec.invoice_ids:
                    if lst.id not in invoice_ids_list:
                       invoice_ids_list.append(lst.id)
                       count_invoice+=1
                     
                    
                _logger.info('s_ordrer')
                
                _logger.info(invoice_ids_list)
                for line in rec.order_line:
                    last_new_timezone = old_timezone.localize(rec.date_order).astimezone(new_timezone)
                    last_new_timezone=last_new_timezone.strftime('%Y-%m-%d')
                    if analytical_account_id:
                        if analytical_account_id==line.analytical_account_id.id:
                                        quantity=quantity+line.product_uom_qty
                                        total_price=total_price+line.price_total
                    else:
                        quantity=quantity+line.product_uom_qty
                        total_price=total_price+line.price_total
                if total_price !=0:
                    sale_orders.append({
                        'name': rec.name,
                        'partner' : rec.partner_id.name,
                        'quantity':quantity,
                        'count_invoice':count_invoice,
                      
                        'total':total_price,   
                        })       
        if date_from:
           date_from=date_from.strftime('%Y-%m-%d')
        if date_to:
           date_to=date_to.strftime('%Y-%m-%d')
        if len(sale_orders)!=0:
            return {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'period' : period_value,
                    'date_from': date_from,
                    'date_to': date_to,
                    'sale_orders' : sale_orders,
                    'total_sale' : total_sale,
                    'customer_name':self.env['res.partner'].search([('id','=',customer)]).name,
                    'data_check':False,
                    'analytical_account_id':self.env['account.analytic.account'].search([('id','=',analytical_account_id)]).name,
                    'name_report':"بيان بحجم المبيعات خلال فتره علي مستوي العملاء"

                }
        else:
            return {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'period' : period_value,
                    'date_from': date_from,
                    'date_to': date_to,
                    'sale_orders' : sale_orders,
                    'total_sale' : total_sale,
                    'customer_name':self.env['res.partner'].search([('id','=',customer)]).name,
                    'data_check':True,
                    'analytical_account_id':self.env['account.analytic.account'].search([('id','=',analytical_account_id)]).name,
                    'name_report':"بيان بحجم المبيعات خلال فتره علي مستوي العملاء"
                }
        # return {
        #     'doc_ids': data['ids'],
        #     'doc_model': data['model'],
        #     'period': period_value,
        #     'date_from': date_from,
        #     'date_to': date_to,
        #     'sale_orders': sale_orders,
        #     'total_sale': total_sale,
        #     'data_check': False
        # }



        



