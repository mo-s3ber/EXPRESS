
from odoo import api, fields, models


class PeriodicalReportProduct(models.TransientModel):
    _name = "box.cheques.in.out"

     
    date_from = fields.Date(string='تاريخ البدء')
    date_to = fields.Date(string='تاريخ الانتهاء')
    partner=fields.Many2one('res.partner','الشريك')
    journal_id=fields.Many2one('account.journal','اليوميه' ,domain="[('type','=','cash')]")



    @api.multi
    def check_report(self):
         
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'partner':self.partner.id,
                'journal_id':self.journal_id.id,



            },
        }
        return self.env.ref('box_in_out.action_report_box_cheques_in_out').report_action(self, data=data)
