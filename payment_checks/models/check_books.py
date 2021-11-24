# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import time
from datetime import date
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree
# from datetime import datetime, date
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

from odoo.osv import expression


class CheckBook(models.Model):
    _name = 'check.book'
    _description = "Checkbooks"

    name = fields.Char(string='Name')
    from_number = fields.Integer()
    to_number = fields.Integer()
    number_next_actual = fields.Integer()
    journal_id = fields.Many2one('account.journal')
    debit_account_id = fields.Many2one('account.account')
    credit_account_id = fields.Many2one('account.account')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_use', 'In Use'),
            ('used', 'Used'),
        ], string='Status', default='draft', readonly=True)

    @api.onchange('from_number')
    def onchange_from_number(self):
        if self.from_number:
            self.number_next_actual = self.from_number


    def set_in_use(self):
        for rec in self:
            rec.state ='in_use'

    def set_used(self):
        for rec in self:
            rec.state = 'used'


