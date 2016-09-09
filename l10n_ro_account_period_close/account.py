# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

class account_account(models.Model):
    _inherit = 'account.account'

    close_check = fields.Boolean('Bypass Closing Side Check',
        help='By checking this when you close a period, it will not respect '
             'the side of closing, meaning: expenses closed on credit side, '
             'incomed closed on debit side. \n You should check the 711xxx '
             'accounts.')

class account_move(models.Model):
    _inherit = 'account.move'

    close_id = fields.Many2one('account.period.closing', 'Closed Account Period')    
         

class account_period_closing(models.Model):
    _name = 'account.period.closing'
    _description = 'Account Period Closing'

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one( 'res.company', string='Company', required=True)
    type = fields.Selection(
        [
            ('income', 'Incomes'),
            ('expense', 'Expenses'),
            ('selected', 'Selected')
        ], string='Type', required=True)
 
    account_ids = fields.Many2many(  'account.account', string='Accounts to close', select=True)
 
    close_result = fields.Boolean('Close debit and credit accounts')
    account_ids = fields.Many2many(
        'account.account', string='Accounts to close', select=True)
 
    debit_account_id = fields.Many2one(
        'account.account',
        'Closing account, debit',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    credit_account_id = fields.Many2one(
        'account.account',
        'Closing account, credit',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    move_ids = fields.One2many('account.move', 'close_id', 'Closing Moves')

    @api.onchange('type')
    def _onchange_type(self):
        account_ids = False
        if self.type and self.type in ('income', 'expense'):
            user_types = self.env['account.account.type'].search( [('code', '=', self.type)])
            self.account_ids = self.env['account.account'].search([
                ('user_type', 'in', [x.id for x in user_types]),
                ('type', '!=', 'view'),
                ('company_id', '=', self.company_id.id)
            ])
        else:
            self.account_ids = account_ids

    @api.one
    def close(self, date=None, period=None, journal=None):
        """ This method will create the closing move for the period selected"""
        if not period or not journal:
            raise UserError('No period or journal defined')
        closing = self[0]
        account_obj = self.env['account.account']
        ctx = dict(self._context)

        if period:
            ctx['period_from'] = period
            ctx['period_to'] = period
        account_ids = closing.account_ids.with_context(ctx)._get_children_and_consol()
        accounts = account_obj.browse(account_ids).with_context(ctx).read(['name', 'balance'])
        move = self.env['account.move'].create({
            'date': date,
            'journal_id': journal,
            'period_id': period,
            'close_id': closing.id,
            'company_id': closing.company_id.id
        })
        amount = 0.0
        for account in accounts:
            if account['balance'] != 0.0:
                check = account_obj.browse(account['id']).close_check
                if closing.type == 'expense' and not check:
                    val = {
                        'name': 'Closing ' + closing.name,
                        'date': date,
                        'move_id': move[0].id,
                        'account_id': account['id'],
                        'credit': account['balance'] or 0.0,
                        'debit': 0.0,
                        'company_id': closing.company_id.id,
                        'journal_id': journal,
                        'period_id': period,
                    }
                elif closing.type == 'income' and not check:
                    val = {
                        'name': 'Closing ' + closing.name,
                        'date': date,
                        'move_id': move[0].id,
                        'account_id': account['id'],
                        'credit': 0.0,
                        'debit': (-1 * account['balance']) or 0.0,
                        'company_id': closing.company_id.id,
                        'journal_id': journal,
                        'period_id': period,
                    }
                else:
                    val = {
                        'name': 'Closing ' + closing.name,
                        'date': date,
                        'move_id': move[0].id,
                        'account_id': account['id'],
                        'credit': account['balance'] > 0.0 and account['balance'] or 0.0,
                        'debit': account['balance'] < 0.0 and -account['balance'] or 0.0,
                        'company_id': closing.company_id.id,
                        'journal_id': journal,
                        'period_id': period,
                    }
                amount += account['balance']
                self.env['account.move.line'].create(val)

        diff_line = {
            'name': 'Closing ' + closing.name,
            'date': date,
            'move_id': move[0].id,
            'account_id': amount >= 0 and closing.debit_account_id.id or closing.credit_account_id.id,
            'credit': amount <= 0.0 and -amount or 0.0,
            'debit': amount >= 0.0 and amount or 0.0,
            'company_id': closing.company_id.id,
            'journal_id': journal,
            'period_id': period,
        }
        self.env['account.move.line'].create(diff_line)
        if self.close_result:
            ctx1 = dict(self._context)
            if period and amount != 0.00:
                period1 = self.env['account.period'].browse(period)
                ctx1.update({'date': False,
                         'fiscalyear': period1.fiscalyear_id.id,
                         'date_from': period1.fiscalyear_id.date_start,
                         'date_to': period1.date_stop})
                debit = closing.debit_account_id.with_context(
                    ctx1).read(['balance'])[0]['balance']
                credit = closing.credit_account_id.with_context(
                    ctx1).read(['balance'])[0]['balance']
                if abs(debit) > abs(credit):
                    new_amount = -1 * credit
                else:
                    new_amount = debit
                old_balance = debit - (-1 * credit)
                debit_acc = closing.debit_account_id
                credit_acc = closing.credit_account_id
                if credit and debit:
                    if old_balance > 0:
                        debit_acc = closing.credit_account_id
                        credit_acc = closing.debit_account_id
                    elif old_balance < 0:
                        debit_acc = closing.debit_account_id
                        credit_acc = closing.credit_account_id
                    diff_line = {
                        'name': 'Closing ' + closing.name + ' ' + str(debit_acc.code),
                        'date': date,
                        'move_id': move[0].id,
                        'account_id': debit_acc.id,
                        'credit': 0.0,
                        'debit': new_amount,
                        'company_id': closing.company_id.id,
                        'journal_id': journal,
                        'period_id': period,
                    }
                    self.env['account.move.line'].create(diff_line)
                    diff_line = {
                        'name': 'Closing ' + closing.name + ' ' + str(credit_acc.code),
                        'date': date,
                        'move_id': move[0].id,
                        'account_id': credit_acc.id,
                        'credit': new_amount,
                        'debit': 0.0,
                        'company_id': closing.company_id.id,
                        'journal_id': journal,
                        'period_id': period,
                    }
                    self.env['account.move.line'].create(diff_line)
        move[0].post()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
