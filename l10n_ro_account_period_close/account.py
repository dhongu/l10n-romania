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


class account_move(models.Model):
    _inherit = 'account.move'

    close_id = fields.Many2one(
        'account.period.closing', 'Closed Account Period')


class account_period_closing(models.Model):
    _name = 'account.period.closing'
    _description = 'Account Period Closing'

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True)
    type = fields.Selection(
        [
            ('income', 'Incomes'),
            ('expense', 'Expenses'),
            ('selected', 'Selected')
        ], string='Type', required=True)
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
            user_types = self.env['account.account.type'].search(
                [('code', '=', self.type)])
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
            raise osv.except_osv('No period or journal defined')
        closing = self[0]
        account_obj = self.env['account.account']
        ctx = dict(self._context)

        if period:
            ctx['period_from'] = period
            ctx['period_to'] = period
        account_ids = closing.account_ids.with_context(
            ctx)._get_children_and_consol()
        accounts = account_obj.browse(account_ids).with_context(
            ctx).read(['name', 'balance'])
        move = self.env['account.move'].create({
            'date': date,
            'journal_id': journal,
            'period_id': period,
            'close_id': closing.id,
            'company_id': closing.company_id.id
        })
        sum = 0.0
        for account in accounts:
            if account['balance'] != 0.0:
                if closing.type == 'expense':
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
                elif closing.type == 'income':
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
                sum += account['balance']
                self.env['account.move.line'].create(val)
        diff_line = {
            'name': 'Closing ' + closing.name,
            'date': date,
            'move_id': move[0].id,
            'account_id': sum >= 0 and closing.debit_account_id.id or closing.credit_account_id.id,
            'credit': sum <= 0.0 and -sum or 0.0,
            'debit': sum >= 0.0 and sum or 0.0,
            'company_id': closing.company_id.id,
            'journal_id': journal,
            'period_id': period,
        }
        self.env['account.move.line'].create(diff_line)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
