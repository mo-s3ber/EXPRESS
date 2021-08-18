from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz

_logger = logging.getLogger(__name__)


class ReportProductSale(models.AbstractModel):
    _name = "report.in_out_payment_cheques.in_out_payment_report_t"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data["form"]["date_from"]
        date_to = data["form"]["date_to"]
        customer = data["form"]["customer"]
        analytical_account_id=data["form"]["analytical_account_id"]


        total_sale = 0.0
        period_value = ""
        domain = []
        if date_from:
            domain.append(("date_invoice", ">=", date_from))
        if date_to:
            domain.append(("date_invoice", "<=", date_to))
        if customer:
            domain.append(("partner_id", "=", customer))

        list = []
        order_line = []
        benging_balance=[]
        partner_list=[]
        move_list=self.env['account.move.line'].search([],order='date asc')
         
        doamin_cheq=[]
        if date_from:
            doamin_cheq.append(("check_payment", ">=", date_from))
        if date_to:
            doamin_cheq.append(("check_payment", "<=", date_to))
        if customer:
            doamin_cheq.append(("investor_id", "=", customer))
         
        cheques_list = []
        order_line = []

        cheques = self.env["check.management"].search(doamin_cheq, order="check_payment,check_date asc")
        _logger.info(cheques)
        for line in cheques:
            if (line.state!='handed'or  line.state!='debited') and line.investor_id.customer==True :
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
        if customer:
            payment_domain.append(("partner_id", "=", customer))
        payments=self.env["account.payment"].search(payment_domain, order="payment_date asc")
        for line in payments:
            if line.payment_type=='inbound'   and line.partner_id.customer==True:
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
        _logger.info('cheques_list')
        _logger.info(cheques_list)
        if len(cheques_list) != 0:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "date_to": date_to,
                "total_sale": total_sale,
                "cheques_list":cheques_list,
                "customer_name": self.env["res.partner"].search([("id", "=", customer)]).name,
                "data_check": False,
                "benging_balance":benging_balance,
               "analytical_account_id":self.env['account.analytic.account'].search([('id','=',analytical_account_id)]).name,
                "name_report":'كشف بالوارد اليومـــي'
            }
        else:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "date_to": date_to,
                "cheques_list":cheques_list,
                "total_sale": total_sale,
                "customer_name": self.env["res.partner"].search([("id", "=", customer)]).name,
                "data_check": True,
                "analytical_account_id":self.env['account.analytic.account'].search([('id','=',analytical_account_id)]).name,
                "benging_balance":benging_balance,
                "name_report":'كشف بالوارد اليومـــي'
            }

