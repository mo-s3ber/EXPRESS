# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.asceticbs.com>
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
#################################################################################

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class ReportInvoices(models.AbstractModel):
    _name = 'report.customer_outstanding_report.invoice_outstanding'

    '''Find Outstanding invoices between the date and find total outstanding amount'''
    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        outstanding_invoice = []
        partners_dict = {}
        partners = self.env['res.partner'].search([('customer','=',True)])
        amount_due = 0
        if partners:
            for partner in partners:
                domain = [('account_id', '=', partner.property_account_receivable_id.id), ('partner_id', '=', partner.id),('date', '>=', docs.start_date),('date', '<=', docs.end_date),('credit', '>', 0), ('debit', '=', 0),('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0)]
                lines = self.env['account.move.line'].search(domain)
                move_line = []
                if lines:
                    for line in lines:
                        move_line.append(line)
                        amount_due += line.amount_residual
                    partners_dict[partner] = move_line
            docs.total_amount_due = abs(amount_due)
            return {
                'docs': docs,
                'partners_dict': partners_dict,
            }
        else:
            raise UserError("There is not any Outstanding invoice")


