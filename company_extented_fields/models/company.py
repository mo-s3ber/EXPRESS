from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Company(models.Model):
    _inherit = 'res.company'


    fax = fields.Char('فاكس')
    commercial_record=fields.Char('سجل تجاري')
    company_info = fields.Text('بيانات إضافية')

