from odoo import api, models,fields
 
class Partner(models.Model):
    _inherit='res.partner'
    analytical_account=fields.Many2one("account.analytic.account",String="الحساب التحليلي ")

    def create_anal(self):


        move_line = self.env['account.move.line'].search([])
        for rec in move_line:
            if rec.account_id == rec.partner_id.property_account_payable_id or rec.account_id == rec.partner_id.property_account_receivable_id:

              if rec.partner_id.analytical_account and not rec.analytic_account_id \
                    :
                 rec.analytic_account_id = rec.partner_id.analytical_account.id
