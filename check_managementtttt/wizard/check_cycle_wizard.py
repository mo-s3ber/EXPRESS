from odoo import models, fields, api, exceptions,_
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError
 
import logging
_logger = logging.getLogger(__name__)

class check_cycle_accs(models.TransientModel):

    _name = 'check.cycle.accounts.default'

    @api.model
    def get_check_lines(self):
        checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
        app_checks = []
        for ch in reversed(checks):
            val = {}
            val['check_number'] = ch.check_number
            val['check_id'] = ch.id
            val['check_amt'] = ch.amount
            val['paid_amt'] = ch.open_amount
            val['open_amt'] = ch.open_amount
            val['check_id']=ch.check_id
            line = self.env['appove.check.lines'].create(val)
            # app_checks.append((0,0, val))
            app_checks.append(line.id)
        return app_checks

    name = fields.Char(default="Please choose the bank Account",readonly=True)
    name_cancel = fields.Char(default="Are you sure you want to cancel the checks", readonly=True)
    name_reject = fields.Char(default="Are you sure you want to reject the checks", readonly=True)
    name_return = fields.Char(default="Are you sure you want to return the checks to company", readonly=True)
    name_vendor = fields.Char(default="Are you sure you want to return the checks to vendor", readonly=True)
    name_approve = fields.Char(default="Please choose the bank Account", readonly=True)
    name_debit = fields.Char(default="Please choose the bank Account", readonly=True)
    name_csreturn = fields.Char(default="Are you sure you want to return the checks to customer", readonly=True)
    name_split_merge = fields.Char(default="Please create the new checks", readonly=True)
    account_id = fields.Many2one('account.account',string="Account")
    journal_id = fields.Many2one('account.journal',string="Journal")
    journal_id_deposit = fields.Many2one('account.journal',string="Journal")
    journal_id_approve = fields.Many2one('account.journal',string="Journal Approve")
    reject_reason = fields.Text(string="Rejection reason")
    approve_check = fields.Many2many('appove.check.lines',ondelete="cascade",default=get_check_lines)
    total_amt_checks = fields.Float(string="total Amount of Checks",compute="getcheckstotamt")
    merge_split_checks = fields.Many2many('split.merge.check',ondelete="cascade")
    bank_deposite=fields.Many2one('res.bank',string="البنك المودع  به")
    new_due_date= fields.Date('تاريخ الاستحقاق الجديد')
    #check_management=fields.One2many('check.management',string="check_management")

    @api.multi
    @api.depends('name_split_merge')
    def getcheckstotamt(self):
        for rec in self:
            rec.total_amt_checks = 0
            checks = rec.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
            for ch in checks:
                rec.total_amt_checks += ch.open_amount

    @api.multi
    def action_save(self):
        if 'action_wiz' in self.env.context:
            if self.env.context['action_wiz'] == 'depoist':
                _logger.info('DEPOIST')
                if not self.journal_id_deposit:
                    raise exceptions.ValidationError(_('Please provide the bank account'))
                if not self.bank_deposite:
                    raise exceptions.ValidationError(_('من فضلك اضف البنك المودع به'))

                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    # if not check.dep_bank:
                    #     raise exceptions.ValidationError(_('Please provide the deposit bank '))
                    # if not check.will_collection_user:
                    #     raise exceptions.ValidationError(_('Please Put Bank Maturity Date For Reporting  '))
                    move = {
                        'name': 'Depoisting Check number ' + check.check_number,
                        'journal_id': self.journal_id_deposit.id,
                        'ref': 'Depoisting Check number ' + check.check_number,
                        'company_id': self.env.user.company_id.id
                    }

                    move_line = {
                        'name': 'Depoisting Check number ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'Depoisting Check number ' + check.check_number,
                    }
                    check.update({'deposited_journal':self.journal_id_deposit.id})
                    if check.check_date:
                         check.update({'new_due_date':check.check_date})
                    if self.new_due_date:
                         check.update({'check_date':self.new_due_date})
                    debit_account = []
                    credit_account = []
                    debit_account.append({'account': self.journal_id_deposit.default_debit_account_id.id, 'percentage': 100})
                     
                    if check.notes_rece_id:
                        credit_account.append({'account': check.notes_rece_id.id, 'percentage': 100})
                    else:
                        credit_account.append({'account': check.unit_id.project_id.NotesReceivableAccount.id, 'percentage': 100})
                    self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id,
                                                               amount=check.open_amount)
                    

                    
                    check.state = 'depoisted'
                    check.bank_deposite=self.bank_deposite
                    check.under_collect_id = self.journal_id_deposit.default_debit_account_id.id
                    check.under_collect_jour = self.journal_id_deposit.id
            elif self.env.context['action_wiz'] == 'approve':
                if not self.journal_id:
                    raise exceptions.ValidationError(_('Please provide the bank account'))
                for approve_ch_line in self.approve_check:
                    z=""
                    for x in self.approve_check:
                        z=z+(str(x.open_amt))+","
                    if approve_ch_line.open_amt < approve_ch_line.paid_amt:
                        raise exceptions.ValidationError(_('The paid amount is greater than open amount for some checks\n'+z))
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    debit_account = []
                    credit_account = []
                    move = {
                        'name': 'Approving Check number ' + check.check_number,
                        'journal_id': self.journal_id.id,
                        'ref': 'Approving Check number ' + check.check_number,
                        'company_id': self.env.user.company_id.id
                    }
                    move_line = {
                        'name': 'Approving Check number ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'Approving Check number ' + check.check_number,
                    }
                    checkamt = check.amount
                    for approve_ch_line in self.approve_check:
                        if approve_ch_line.check_id == check.id:
                            checkamt = approve_ch_line.paid_amt
                            check.open_amount -= approve_ch_line.paid_amt
                    if check.investor_id:
                        debit_account.append({'account': self.journal_id.default_debit_account_id.id, 'percentage': 100})
                        if check.under_collect_id:
                            credit_account.append({'account': check.deposited_journal.default_credit_account_id.id, 'percentage': 100})
                        else:
                            credit_account.append({'account': check.deposited_journal.default_credit_account_id.id, 'percentage': 100})


                        if check.state == 'returned':
                            if check.notes_rece_id:
                                credit_account.append({'account': check.notes_rece_id.id, 'percentage': 100})
                            else:
                                credit_account.append(
                                    {'account': check.unit_id.project_id.NotesReceivableAccount.id, 'percentage': 100})
                        
                    if checkamt > 0.0:
                        self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id,
                                                               amount=checkamt)
                    check.state = 'approved'
                 
            elif self.env.context['action_wiz'] == 'reject':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    check.state = 'rejected'
                    message = "Rejection Reason is " + str(self.reject_reason)
                    check.message_post(body=message)
            elif self.env.context['action_wiz'] == 'return':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    move = {
                        'name': 'Returning Check number ' + check.check_number,
                        'journal_id': check.under_collect_jour.id,
                        'ref': 'Returning Check number ' + check.check_number,
                        'company_id': self.env.user.company_id.id
                    }
                    _logger.info('Rejected')
                    _logger.info(check.investor_id.id)
                     


                    move_line = {
                        'name': 'Returning Check number ' + check.check_number,
                        'partner_id':  check.investor_id.id,
                        'ref': 'Returning Check number ' + check.check_number,
                    }
                    debit_account = []
                    credit_account = []
                    credit_account.append({'account': check.under_collect_jour.default_debit_account_id.id, 'percentage': 100})
                    if check.notes_rece_id:
                        debit_account.append({'account': check.notes_rece_id.id, 'percentage': 100})
                    else:
                        debit_account.append({'account': check.unit_id.project_id.NotesReceivableAccount.id, 'percentage': 100})
                    self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id,
                                                               amount=check.open_amount)
                    check.state = 'returned'

            elif self.env.context['action_wiz'] == 'debit':
                _logger.info('DEBIT')
                if not self.journal_id:
                    raise exceptions.ValidationError(_('Please provide the bank account'))
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    check.under_debited = self.journal_id.id
                    move = {
                        'name': 'Debiting Check number ' + check.check_number,
                        'journal_id': self.journal_id.id,
                        'ref': 'Debiting Check number ' + check.check_number,
                        'company_id': self.env.user.company_id.id
                    }
                    move_line = {
                        'name': 'Debiting Check number ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'Debiting Check number ' + check.check_number,
                    }


                    debit_account = []
                    credit_account = []
                    credit_account.append({'account': self.journal_id.default_credit_account_id.id, 'percentage': 100})
                    debit_account.append({'account': check.notespayable_id.id, 'percentage': 100})
                    self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id,
                                                              amount=check.amount)
                    debit_account = []
                    credit_account = []
                    
                    check.state = 'debited'
                    check.open_amount == 0.0
            elif self.env.context['action_wiz'] == 'return_hand':
                 
                
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                account_handed=''
                for check in checks:
                    account_id = self.env['native.payments.check.create'].search([('id','=',check.check_id)]).nom_pay_id
                    
                    if check.under_debited:
                        journal=check.under_debited.id

                    else:
                        journal=self.journal_id.id
                    if not journal:
                          raise exceptions.ValidationError(_('Please provide the bank account'))
                        
                    move = {
                        'name': 'return  Check number to handed' + check.check_number,
                        'journal_id': journal,
                        'ref': 'return  Check number to handed ' + check.check_number,
                        'company_id': self.env.user.company_id.id
                    }
                    move_line = {
                        'name': 'return  Check number to handed ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'return  Check number to handed ' + check.check_number,
                    }

                    
                    debit_account = []
                    credit_account = []
                   
                    journal=self.env["account.journal"].search([('id','=',journal)])
                    credit_account.append({'account': check.notespayable_id.id, 'percentage': 100})
                    debit_account.append({'account':journal.default_credit_account_id.id , 'percentage': 100})
                    self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id,
                                                              amount=check.amount)
                    debit_account = []
                    credit_account = []
                    
                    check.state = 'handed'
                    check.open_amount == 0.0
            elif self.env.context['action_wiz'] == 'return_cst':
                _logger.info('return_handed')
                 
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                
                for check in checks:
                    journal_id = self.env['native.payments.check.create'].search([('id','=',check.check_id)]).nom_pay_id
                   
                    move = {
                        'name': 'Return  Check number to handed ' + check.check_number,
                        'journal_id':journal_id.payment_method.id,
                        'ref': 'Return  Check number to handed ' + check.check_number,
                        'company_id': self.env.user.company_id.id
                    }
                    move_line = {
                        'name': 'Return  Check number to handed ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'Return  Check number to handed ' + check.check_number,
                    }


                    debit_account = []
                    credit_account = []
                    
                    credit_account.append({'account': journal_id.account_id.id, 'percentage': 100})
                    debit_account.append({'account': journal_id.payment_method.default_debit_account_id.id, 'percentage': 100})
                    self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id,
                                                              amount=check.amount)
                    debit_account = []
                    credit_account = []
                    
                    check.state = 'vendor_return'
                    check.open_amount == 0.0               
            elif self.env.context['action_wiz'] == 'cs_return':
                _logger.info('CS return')

                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                
                for check in checks:
                    journal_id = self.env['native.payments.check.create'].search([('id','=',check.check_id)]).nom_pay_id
                    _logger.info(journal_id)
                    _logger.info(journal_id.payment_method)
                    _logger.info(journal_id.account_id)

                    move = {
                        'name': 'Returning Check number ' + check.check_number + ' to customer',
                        'journal_id': journal_id.payment_method.id,
                        'ref': 'Returning Check number ' + check.check_number + ' to customer',
                        'company_id': self.env.user.company_id.id,

                    }
                    move_line = {
                        'name': 'Returning Check number ' + check.check_number + ' to customer',
                        'partner_id': check.investor_id.id,
                        'ref': 'Returning Check number ' + check.check_number + ' to customer',
                    }

                    if check.investor_id:
                        debit_account = [{'account':journal_id.account_id.id , 'percentage' : 100}]
                        credit_account = [{'account': journal_id.payment_method.default_credit_account_id.id,'percentage' : 100}]
                        self.env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                                   debit_account=debit_account,
                                                                   credit_account=credit_account,
                                                                   src_currency=self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id,
                                                                   amount=check.amount)


                    check.state = 'cs_return'
                    check.check_state = 'suspended'
            elif self.env.context['action_wiz'] == 'split_merge':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                _logger.info(checks.investor_id)
                _logger.info(checks)
                for x in checks:
                    if not x.notes_rece_id:
                        raise exceptions.ValidationError(_('Action not allowed on normal checks'))
                new_tot_amt = 0
                notes_rece_id = 0
                ch_state = 'holding'
                check_payment=''
                check_id=0
                if checks[0]:

                    notes_rece_id = checks[0].notes_rece_id.id
                    ch_state = checks[0].state
                    check_payment=checks[0].check_payment
                    _logger.info('Check Payment Date')
                    _logger.info(check_payment)
                    check_id=checks[0].check_id
                else:
                    raise exceptions.ValidationError(_('Action not allowed on normal checks'))
                for ch in checks:
                    if notes_rece_id != ch.notes_rece_id.id:
                        raise exceptions.ValidationError(
                            _('You can not merge checks from different journals'))
                for sp_mr_checks in self.merge_split_checks:
                    new_tot_amt += sp_mr_checks.amount
                if new_tot_amt != self.total_amt_checks:
                    raise exceptions.ValidationError(_('Amount of new Checks is not equal to amount of selected checks'))

                for sp_mr_checks in self.merge_split_checks:
                    check_line_val = {}
                    check_line_val['check_number'] = sp_mr_checks.check_number
                    check_line_val['check_date'] = sp_mr_checks.check_date
                    check_line_val['check_bank'] = sp_mr_checks.bank.id
                    check_line_val['dep_bank'] = sp_mr_checks.dep_bank.id
                    check_line_val['amount'] = sp_mr_checks.amount
                    check_line_val['open_amount'] = sp_mr_checks.amount
                    _logger.info('PARTNER')
                    _logger.info(checks.investor_id)
                    check_line_val['investor_id'] = checks.investor_id.id
                    check_line_val['amount_res'] = 0
                    check_line_val['amount_con'] = 0
                    check_line_val['amount_gar'] = 0
                    check_line_val['amount_mod'] = 0
                    check_line_val['amount_ser'] = 0
                    check_line_val['amount_reg'] = 0
                    check_line_val['state'] = ch_state
                    check_line_val['type'] = 'regular'
                    check_line_val['check_type'] = checks.check_type
                    check_line_val['notes_rece_id'] = notes_rece_id
                    check_line_val['notespayable_id'] = notes_rece_id
                    check_line_val['check_payment']=check_payment 
                    check_line_val['check_id']=check_id
                    new_check = self.env['check.management'].create(check_line_val)
                for x in checks:
                    x.unlink()
        else:
            raise exceptions.ValidationError(_('Unknown Action'))
        return True

    @api.model
    def create(self,vals):
        _logger.info('craeet new line')
        return super(check_cycle_accs,self).create(vals)




class approve_check_lines(models.Model):

    _name = 'appove.check.lines'

    check_number = fields.Char()
    check_id = fields.Integer()
    check_amt = fields.Float()
    paid_amt = fields.Float()
    open_amt = fields.Float()


class split_merge_check(models.Model):

    _name = 'split.merge.check'
    _order = 'check_number asc'

    check_number = fields.Char(string=_("Check number"),required=True)
    check_date = fields.Date(string=_('Check Date'),required=True)
    amount = fields.Float(string=_('Amount'),required=True)
    bank = fields.Many2one('res.bank',string=_("Check Bank Name"))
    dep_bank = fields.Many2one('res.bank',string=_("Depoist Bank"))
    partner_id = fields.Many2one("res.partner", string="Customer Name", )