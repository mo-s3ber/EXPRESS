
from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging

_logger = logging.getLogger(__name__)


class ReportProductSale(models.AbstractModel):
    _name = "report.vendor_statement_t.vendor_statement_report_t"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        vendor=data['form']['vendor']
        analytical_account_id=data['form']['analytical_account_id']
         
        total_sale = 0.0
        period_value = ''
        domain=[]
        if date_from:
            domain.append(('date_invoice', '>=', date_from))
        if date_to  :
            domain.append(('date_invoice', '<=', date_to))
        if vendor:
            domain.append(('partner_id', '=', vendor))

         
        list = []
        order_line=[]
        benging_balance=[]
        partner_list=[]
        move_list=self.env['account.move.line'].search([],order='date asc')
        for rec in move_list:
            partner_list.append(rec.partner_id.id)

        partner_list=set(partner_list)
        _logger.info(partner_list)
        for part in partner_list:
            check=False
            for line in move_list:
                partner_name=line.partner_id.name
                if part==line.partner_id.id and line.move_id.begin_balance==True and check==False:
                    if line.partner_id.property_account_payable_id==line.account_id or  line.partner_id.property_account_receivable_id==line.account_id:
                        
                        benging_balance.append({
                          'partner':line.partner_id.name,
                          'debit':line.debit,
                          'credit':line.credit,
                        
                        })
                        check=True
                        break
                    
            if check==False:
                benging_balance.append({
                          'partner':self.env['res.partner'].search([('id','=',part)]).name,
                          'debit':0,
                          'credit':0,
                        
                        })


        invoice_ids = self.env['account.invoice'].search(domain,order='date_invoice asc')
         
      
        for inv in invoice_ids:
                if inv.state!='cancel' and ( inv.type== "in_invoice" ):
                        date_so=''
                        
                        sale_order=self.env['purchase.order'].search([('name','=',inv.origin)])
                        if sale_order:
                            date_so=sale_order.date_order
                        q=1
                
                        if inv.type== "in_refund":
                            q=-1    

                        for line in inv.invoice_line_ids:
                                if  analytical_account_id:
                                     if line.account_analytic_id.id == analytical_account_id: 
                                         list.append({
                                            'so_number':inv.origin,
                                            'date_so': date_so,
                                            'invoice_number':line.invoice_id.number,
                                            
                                            'product_id':line.product_id.name,
                                            'inv_name':line.invoice_id.name,
                                            'date_in':line.invoice_id.date_invoice,
                                            'partner' : line.invoice_id.partner_id.name,
                                            'quantity':line.quantity,
                                            'price_unit':line.price_unit*q,
                                            'total':line.price_total*q,
                                            'note_invoice':line.note_invoice,
                                            "inv_type":inv.type


                                        })
                                else:
                                    list.append({
                                            'so_number':inv.origin,
                                            'date_so': date_so,
                                            'invoice_number':line.invoice_id.number,
                                            
                                            'product_id':line.product_id.name,
                                            'inv_name':line.invoice_id.name,
                                            'date_in':line.invoice_id.date_invoice,
                                            'partner' : line.invoice_id.partner_id.name,
                                            'quantity':line.quantity,
                                            'price_unit':line.price_unit*q,
                                            'total':line.price_total*q,
                                            'note_invoice':line.note_invoice,
                                            "inv_type":inv.type


                                        })
        doamin_cheq=[]
        if date_from:
            doamin_cheq.append(("check_payment", ">=", date_from))
        if date_to:
            doamin_cheq.append(("check_payment", "<=", date_to))
        if vendor:
            doamin_cheq.append(("investor_id", "=", vendor))
         
        cheques_list = []
        order_line = []

        cheques = self.env["check.management"].search(doamin_cheq,order="check_payment,check_date asc")
        _logger.info(cheques)
        for line in cheques:
            if line.state in ('debited','handed'):
                if line.investor_id.supplier==True:
                    id_payement=self.env['native.payments.check.create'].search([('check_number','=',line.check_number)]).id
                    cheques_list.append(
                        {
                            "cheque_number": line.check_number,
                            "cheque_date": line.check_date,
                            "check_payment": line.check_payment,
                            "partner": line.investor_id.name,
                            "state": line.state,
                            "check_bank": line.check_bank.name,
                            "dept_bank":line.dep_bank.name,
                            "total": line.amount,
                            'id_payement':id_payement
                        }
                )
        payment_domain=[]
        if date_from:
            payment_domain.append(("payment_date", ">=", date_from))
        if date_to:
            payment_domain.append(("payment_date", "<=", date_to))
        if vendor:
            payment_domain.append(("partner_id", "=", vendor))
        payments=self.env["account.payment"].search(payment_domain, order="payment_date asc")
        for line in payments:
            if line.partner_id.supplier==True and line.state=='posted' and line.payment_type=='outbound':
                cheques_list.append(
                    {
                        "cheque_number": 'نــــقدا',
                        "cheque_date": line.payment_date,
                        "check_payment": line.payment_date,
                        "partner": line.partner_id.name,
                        "state": '',
                        "check_bank": '',
                        "total": line.amount,
                        'id_payement':line.id
                    }
            )
        if len(list)!=0 or len(cheques_list) !=0:

            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'period' : period_value,
                'date_from': date_from,
                'date_to': date_to,
                'sale_orders' : list,
                'total_sale' : total_sale,
                'vendor_name':self.env['res.partner'].search([('id','=',vendor)]).name,
                'data_check':False,
                'cheques_list':cheques_list,
                'benging_balance':benging_balance,
                "analytical_account_id":self.env['account.analytic.account'].search([('id','=',analytical_account_id)]).name,

                "name_report":'Tكشــف حســـاب مــــــورد'
            }
        else:
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'period' : period_value,
                'date_from': date_from,
                'date_to': date_to,
                'sale_orders' : list,
                'total_sale' : total_sale,
                'vendor_name':self.env['res.partner'].search([('id','=',vendor)]).name,
                'data_check':True,
                'cheques_list':cheques_list,
                'benging_balance':benging_balance,
                "analytical_account_id":self.env['account.analytic.account'].search([('id','=',analytical_account_id)]).name,
                "name_report":'Tكشــف حســـاب مــــــورد'
            }
            
