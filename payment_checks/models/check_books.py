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
    form = fields.Integer()
    to = fields.Integer()
    prefix = fields.Char()
    padding = fields.Integer()
    journal_id = fields.Many2one('account.journal')
    debit_journal_id = fields.Many2one('account.journal')
    sequence_id = fields.Many2one('ir.sequence')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_use', 'In Use'),
            ('used', 'Used'),
        ], string='Status', default='draft', readonly=True)

    def set_in_use(self):
        for rec in self:
            sequence_id = rec.sequence_id.create(
                {'name': rec.name,
                 'code': rec.journal_id.code,
                 'prefix': rec.prefix,
                 'padding': rec.padding,
                 'active': True})
            rec.sequence_id = sequence_id.id
            rec.state ='in_use'

    def set_used(self):
        for rec in self:
            rec.sequence_id.active = False
            rec.state = 'used'


