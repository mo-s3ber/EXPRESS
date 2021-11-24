from odoo import fields, api, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    checks_ids = fields.One2many('payment.check','payment_id')
    check_type = fields.Selection(
        [
            ('issue', 'Issue'),
            ('receive', 'Receive'),
        ], string='Type')
    is_check = fields.Boolean()

    @api.onchange('checks_ids')
    def onchange_checks_ids(self):
        amount = 0.0
        for check in self.checks_ids:
            amount += check.amount
        self.amount = amount


    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id.check_type in ['issue','receive']:
            self.is_check = True


    @api.onchange('payment_type')
    def onchange_check_payment_type(self):
        if self.payment_type == 'inbound':
            self.check_type = 'receive'
        if self.payment_type == 'outbound':
            self.check_type = 'issue'


    @api.depends('journal_id', 'payment_type', 'payment_method_line_id')
    def _compute_outstanding_account_id(self):
        for pay in self:
            if pay.payment_type == 'inbound':
                if pay.check_type == 'receive' and pay.is_check:
                    pay.outstanding_account_id = pay.journal_id.holding_check_account_id
                else:
                    pay.outstanding_account_id = (pay.payment_method_line_id.payment_account_id
                                                  or pay.journal_id.company_id.account_journal_payment_debit_account_id)
            elif pay.payment_type == 'outbound':
                if pay.check_type == 'issue' and pay.is_check:
                    pay.outstanding_account_id = pay.journal_id.handed_check_account_id
                else:
                    pay.outstanding_account_id = (pay.payment_method_line_id.payment_account_id
                                              or pay.journal_id.company_id.account_journal_payment_credit_account_id)
            else:
                pay.outstanding_account_id = False


    def _get_valid_liquidity_accounts(self):
        return (
            self.journal_id.default_account_id,
            self.payment_method_line_id.payment_account_id,
            self.journal_id.holding_check_account_id,
            self.journal_id.handed_check_account_id,
            self.journal_id.company_id.account_journal_payment_debit_account_id,
            self.journal_id.company_id.account_journal_payment_credit_account_id,
            self.journal_id.inbound_payment_method_line_ids.payment_account_id,
            self.journal_id.outbound_payment_method_line_ids.payment_account_id,
        )

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for payment in self.filtered(
            lambda p: p.check_type == 'receive' and p.is_check == True):
            for check in payment.checks_ids:
                check.button_holding()
        for payment in self.filtered(
            lambda p: p.check_type == 'issue' and p.is_check == True):
            for check in payment.checks_ids:
                check.button_handed()
        return res