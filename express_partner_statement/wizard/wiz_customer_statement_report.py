# -*- coding: utf-8 -*-


from odoo import api, fields, models


class PeriodicalReportProduct(models.TransientModel):
    _name = "customer.statement"

    date_from = fields.Date(string='تاريخ البدء')
    date_to = fields.Date(string='تاريخ الانتهاء')
    customer = fields.Many2one('res.partner', 'العميل', domain="[('customer','=',True)]")
    analytical_account_id = fields.Many2one('account.analytic.account', string="الحساب التحليلي")

    @api.multi
    def check_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'customer': self.customer.id,
                'analytical_account_id':self.analytical_account_id.id,

            },
        }
        return self.env.ref('express_partner_statement.action_report_customer_inv_statement').report_action(self, data=data)
