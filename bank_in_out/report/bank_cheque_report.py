
from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz
_logger = logging.getLogger(__name__)


class ReportProductSale(models.AbstractModel):
    _name = "report.bank_in_out.bank_cheques_report_in_out"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from =data["form"]["date_from"]
        date_to =  data["form"]["date_to"]
        partner = data["form"]["partner"]
        journal_id = data["form"]["journal_id"]
        journal_list,ids,domain=[],[],[]
        if date_from:
            date_from= date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()

        if date_to:
            date_to = datetime.datetime.strptime(data["form"]["date_to"], '%Y-%m-%d').date()

        domain.append(('journal_id.type', '=', 'bank'))
        if partner:
            domain.append(('partner_id', '=', partner))
        if journal_id:
            domain.append(('journal_id', '=', journal_id))



        move_lines = self.env['account.move.line'].search(domain,order='date asc')

        if date_from or date_to:
            for rec in move_lines:


                if date_to and date_from:
                    if date_from<= rec.date and date_to >= rec.date:
                        ids.append(rec.id)
                elif date_from:
                    if date_from <= rec.date:
                        ids.append(rec.id)
                elif date_to:
                    if date_to >= rec.date:
                        ids.append(rec.id)

            if ids:
                move_lines = self.env["account.move.line"].search([('id', 'in', ids)],order='date asc')
            else:
                move_lines = []
        lines=[]
        for rec in move_lines:
            amount_debit,amount_credit=0,0
            if rec.journal_id not in journal_list and rec.journal_id.type=='bank':
                journal_list.append(rec.journal_id)
            if rec.account_id == rec.journal_id.default_debit_account_id :
                amount_debit=rec.debit
                lines.append({'partner_id': rec.partner_id, 'journal_id': rec.journal_id, 'date': rec.date
                                 , 'amount_credit': rec.credit, 'amount_debit': rec.debit})


            elif rec.account_id == rec.journal_id.default_credit_account_id:
                amount_credit = rec.credit
                lines.append({'partner_id': rec.partner_id, 'journal_id': rec.journal_id, 'date': rec.date
                                 ,'amount_credit': rec.credit, 'amount_debit': rec.debit})





        return {
            "doc_ids": data["ids"],
            "doc_model": data["model"],
            "journal_list":journal_list,

            "date_from": date_from,
            "date_to": date_to,
             "lines":lines,
            "name_report":'كشف حساب بنك '
        }


