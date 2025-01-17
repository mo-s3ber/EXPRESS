
from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging

_logger = logging.getLogger(__name__)


class ReportProductSale(models.AbstractModel):
    _name = "report.bank_cheques.bank_cheques_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data["form"]["date_from"]
        date_to = data["form"]["date_to"]
        partner = data["form"]["partner"]
        bank = data["form"]["bank"]
        deposit_bank = data["form"]["deposit_bank"]
        state = data["form"]["state"]
        issue_type=data["form"]["issue_type"]
        rec_type=data["form"]["rec_type"]
        due_date_from=data["form"]["due_date_from"]
        due_date_to=data["form"]["due_date_to"]

        total_sale = 0.0
        period_value = ""
        domain = []
        if date_from:
            domain.append(("check_payment", ">=", date_from))
        if date_to:
            domain.append(("check_payment", "<=", date_to))
        if partner:
            domain.append(("investor_id", "=", partner))
        if bank:
            domain.append(("check_bank", "=", bank))
        if state:
            domain.append(("state", "=", state))
        if due_date_to:
            domain.append(("check_date", "<=", due_date_to))
        if due_date_from:
            domain.append(("check_date", ">=", due_date_from))
        if deposit_bank:
            domain.append(("bank_deposite", "=", deposit_bank))
        if issue_type:
            domain.append(("check_type", "=", 'pay'))
        else:
            domain.append(("check_type", "=", 'rece'))
         
        list = []
        order_line = []
        cheques = self.env["check.management"].search(domain, order="check_payment,check_date asc")
        user_log=self.env['res.users'].search([('id','=',self.env.uid)])
        state_value=''
        for line in cheques:
            if user_log.lang=='en_US':
                    state_value=line.state
            elif user_log.lang=='ar_SY' or user_log.lang=='ar_AA':
                if line.state=='holding':
                    state_value='الخزنه'
                elif line.state=='depoisted':
                    state_value='تحت التحصيل'
                elif line.state=='approved':
                    state_value='معتـــــمدة'
                elif line.state=='rejected':
                    state_value='المرفـــوضه'
                elif line.state=='returned':
                    state_value='المرتجعه'
                elif line.state=='handed':
                    state_value='الصـــادره'
                elif line.state=='debited':
                    state_value='المــدينــه'
                elif line.state=='canceled':
                    state_value=line.state
                elif line.state=='cs_return':
                    state_value='المرتـــجعه للعميل'
            list.append(
                {
                    "cheque_number": line.check_number,
                    "cheque_date": line.check_date,
                    "check_payment": line.check_payment,
                    "partner": line.investor_id.name,
                    "state": state_value,
                    "check_bank": line.check_bank.name,
                    "dept_bank":line.dep_bank.name,
                    "total": line.amount,
                    "bank_deposite":line.bank_deposite.name,
                    "name":self.env['native.payments.check.create'].search([('id','=',line.check_id)]).nom_pay_id.name_check
                }
            )
        ch_name=''
        state_value=''
        if issue_type==False:
            ch_name="customer_name"
        else:
            ch_name="vendor_name"

        if state=='holding':
                    state_value='الخزنه'
        elif state=='depoisted':
            state_value='تحت التحصيل'
        elif state=='approved':
            state_value='معتـــــمدة'
        elif state=='rejected':
            state_value='المرفـــوضه'
        elif state=='returned':
            state_value='المرتجعه'
        elif state=='handed':
            state_value='الصـــادره'
        elif state=='debited':
            state_value='المــدينــه'
        elif state=='canceled':
            state_value='ملغيه'
        elif state=='cs_return':
            state_value='المرتـــجعه للعميل'
        if len(list) != 0:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "date_to": date_to,
                "due_date_from": due_date_from,
                "due_date_to": due_date_to,
                "deposit_bank":self.env["res.bank"].search([("id", "=", deposit_bank)]).name,
                "cheques": list,
                "total_sale": total_sale,
                "bank": self.env["res.bank"].search([("id", "=", bank)]).name,
                ch_name: self.env["res.partner"].search([("id", "=", partner)]).name,
                "state": state_value,
                "data_check": False,
                "issue_type":issue_type,

                "name_report":'بيان بشيــــــكات البنك'
            }
        else:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "deposit_bank":self.env["res.bank"].search([("id", "=", deposit_bank)]).name,
                "date_to": date_to,
                "due_date_from": due_date_from,
                "due_date_to": due_date_to,
                "cheques": list,
                "total_sale": total_sale,
                "bank": self.env["res.bank"].search([("id", "=", bank)]).name,
                ch_name: self.env["res.partner"].search([("id", "=", partner)]).name,
                "state": state_value,
                "data_check": True,
                "issue_type":issue_type,
                "name_report":'بيان بشيــــــكات البنك'
            }

