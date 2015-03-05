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

from openerp import models, fields, _


class account_statement_operation_template(models.Model):
    _inherit = 'account.statement.operation.template'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True)

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class account_bank_statement_line(osv.osv):
    _inherit = "account.bank.statement.line"

    def process_reconciliation(self, cr, uid, id, mv_line_dicts, context=None):
        """ Creates a move line for each item of mv_line_dicts and for the statement line. Reconcile a new move line with its counterpart_move_line_id if specified. Finally, mark the statement line as reconciled by putting the newly created move id in the column journal_entry_id.

            :param int id: id of the bank statement line
            :param list of dicts mv_line_dicts: move lines to create. If counterpart_move_line_id is specified, reconcile with it
        """
        if context is None:
            context = {}
        st_line = self.browse(cr, uid, id, context=context)
        company_currency = st_line.journal_id.company_id.currency_id
        statement_currency = st_line.journal_id.currency or company_currency
        bs_obj = self.pool.get('account.bank.statement')
        am_obj = self.pool.get('account.move')
        aml_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')

        # Checks
        if st_line.journal_entry_id.id:
            raise osv.except_osv(
                _('Error!'), _('The bank statement line was already reconciled.'))
        for mv_line_dict in mv_line_dicts:
            for field in ['debit', 'credit', 'amount_currency']:
                if field not in mv_line_dict:
                    mv_line_dict[field] = 0.0
            if mv_line_dict.get('counterpart_move_line_id'):
                mv_line = aml_obj.browse(
                    cr, uid, mv_line_dict.get('counterpart_move_line_id'), context=context)
                if mv_line.reconcile_id:
                    raise osv.except_osv(
                        _('Error!'), _('A selected move line was already reconciled.'))

        # Create the move
        move_name = (st_line.statement_id.name or st_line.name) + \
            "/" + str(st_line.sequence)
        move_vals = bs_obj._prepare_move(
            cr, uid, st_line, move_name, context=context)
        move_id = am_obj.create(cr, uid, move_vals, context=context)

        # Create the move line for the statement line
        if st_line.statement_id.currency.id != company_currency.id:
            if st_line.currency_id == company_currency:
                amount = st_line.amount_currency
            else:
                ctx = context.copy()
                ctx['date'] = st_line.date
                amount = currency_obj.compute(
                    cr, uid, st_line.statement_id.currency.id, company_currency.id, st_line.amount, context=ctx)
        else:
            amount = st_line.amount
        to_create = []
        if st_line.currency_id and st_line.amount_currency and st_line.currency_id.id == company_currency.id:
            ctx = context.copy()
            ctx['date'] = datetime.strptime(st_line.statement_id.date, "%Y-%m-%d")
            amount_currency = currency_obj.compute(
                cr, uid, statement_currency.id, company_currency.id, st_line.amount, context=ctx)
            if amount - amount_currency:
                currency_diff = amount_currency - amount
                to_create.append(self.get_currency_rate_line(
                            cr, uid, st_line, currency_diff, move_id, context=context))
                amount = amount_currency
        bank_st_move_vals = bs_obj._prepare_bank_move_line(
            cr, uid, st_line, move_id, amount, company_currency.id, context=context)
        aml_obj.create(cr, uid, bank_st_move_vals, context=context)
        # Complete the dicts
        st_line_currency = st_line.currency_id or statement_currency
        st_line_currency_rate = st_line.currency_id and (
            st_line.amount_currency / st_line.amount) or False
        for mv_line_dict in mv_line_dicts:
            if mv_line_dict.get('is_tax_line'):
                continue
            mv_line_dict['ref'] = move_name
            mv_line_dict['move_id'] = move_id
            mv_line_dict['period_id'] = st_line.statement_id.period_id.id
            mv_line_dict['journal_id'] = st_line.journal_id.id
            mv_line_dict['company_id'] = st_line.company_id.id
            mv_line_dict['statement_id'] = st_line.statement_id.id
            if mv_line_dict.get('counterpart_move_line_id'):
                mv_line = aml_obj.browse(
                    cr, uid, mv_line_dict['counterpart_move_line_id'], context=context)
                mv_line_dict[
                    'partner_id'] = mv_line.partner_id.id or st_line.partner_id.id
                mv_line_dict['account_id'] = mv_line.account_id.id
                invoice = mv_line.invoice
                for acc_move_line in invoice.move_id.line_id:
                    if acc_move_line.real_tax_code_id:
                        # compute the VAT or base line proportionally to the
                        # paid amount
                        pay_amount = mv_line_dict[
                            'credit'] or mv_line_dict['debit']
                        new_line_amount = currency_obj.round(
                            cr, uid, company_currency, (pay_amount / invoice.amount_total) * acc_move_line.tax_amount)
                        acc = acc_move_line.real_account_id and acc_move_line.real_account_id.id or acc_move_line.account_id.id
                        # prepare the real move line
                        vals = {
                            'name': invoice.number + ' - ' + acc_move_line.name,
                            'account_id': acc,
                            'credit': acc_move_line.credit and new_line_amount or 0.0,
                            'debit': acc_move_line.debit and new_line_amount or 0.0,
                            'date': st_line.date,
                            'partner_id': acc_move_line.partner_id and acc_move_line.partner_id.id or False,
                            'tax_code_id': acc_move_line.real_tax_code_id.id,
                            'tax_amount': new_line_amount,
                            'move_id': move_id,
                            'statement_id': st_line.statement_id.id
                        }
                        if acc_move_line.product_id:
                            vals['debit'] = vals['credit'] = 0.00
                        to_create.append(vals)
                        # prepare the shadow move line
                        vals = {
                            'name': invoice.number + ' - ' + acc_move_line.name,
                            'account_id': acc_move_line.account_id.id,
                            'credit': acc_move_line.debit and new_line_amount or 0.0,
                            'debit': acc_move_line.credit and new_line_amount or 0.0,
                            'date': st_line.date,
                            'partner_id': acc_move_line.partner_id and acc_move_line.partner_id.id or False,
                            'tax_code_id': acc_move_line.tax_code_id.id,
                            'tax_amount': -new_line_amount,
                            'move_id': move_id,
                            'statement_id': st_line.statement_id.id
                        }
                        if acc_move_line.product_id:
                            vals['debit'] = vals['credit'] = 0.00
                        to_create.append(vals)
            if st_line_currency.id != company_currency.id:
                ctx = context.copy()
                ctx['date'] = st_line.date
                mv_line_dict['amount_currency'] = mv_line_dict[
                    'debit'] - mv_line_dict['credit']
                mv_line_dict['currency_id'] = st_line_currency.id
                if st_line.currency_id and statement_currency.id == company_currency.id and st_line_currency_rate:
                    debit_at_current_rate = self.pool.get('res.currency').round(
                        cr, uid, company_currency, mv_line_dict['debit'] / st_line_currency_rate)
                    credit_at_current_rate = self.pool.get('res.currency').round(
                        cr, uid, company_currency, mv_line_dict['credit'] / st_line_currency_rate)
                elif st_line.currency_id and st_line_currency_rate:
                    debit_at_current_rate = currency_obj.compute(
                        cr, uid, statement_currency.id, company_currency.id, mv_line_dict['debit'] / st_line_currency_rate, context=ctx)
                    credit_at_current_rate = currency_obj.compute(
                        cr, uid, statement_currency.id, company_currency.id, mv_line_dict['credit'] / st_line_currency_rate, context=ctx)
                else:
                    debit_at_current_rate = currency_obj.compute(
                        cr, uid, st_line_currency.id, company_currency.id, mv_line_dict['debit'], context=ctx)
                    credit_at_current_rate = currency_obj.compute(
                        cr, uid, st_line_currency.id, company_currency.id, mv_line_dict['credit'], context=ctx)
                if mv_line_dict.get('counterpart_move_line_id'):
                    # post an account line that use the same currency rate than
                    # the counterpart (to balance the account) and post the
                    # difference in another line
                    if datetime.strptime(mv_line.date, "%Y-%m-%d").month == datetime.strptime(st_line.date, "%Y-%m-%d").month:
                        # get current currency rate
                        date1 = datetime.strptime(mv_line.date, "%Y-%m-%d")
                    else:
                        date1 = datetime.strptime(
                            st_line.statement_id.period_id.date_start, "%Y-%m-%d")
                    ctx['date'] = date1
                    debit_at_old_rate = currency_obj.compute(
                        cr, uid, st_line_currency.id, company_currency.id, mv_line_dict['debit'], context=ctx)
                    credit_at_old_rate = currency_obj.compute(
                        cr, uid, st_line_currency.id, company_currency.id, mv_line_dict['credit'], context=ctx)
                    mv_line_dict['credit'] = credit_at_old_rate
                    mv_line_dict['debit'] = debit_at_old_rate
                    if debit_at_old_rate - debit_at_current_rate:
                        currency_diff = debit_at_current_rate - \
                            debit_at_old_rate
                        to_create.append(self.get_currency_rate_line(
                            cr, uid, st_line, -currency_diff, move_id, context=context))
                    if credit_at_old_rate - credit_at_current_rate:
                        currency_diff = credit_at_current_rate - \
                            credit_at_old_rate
                        to_create.append(self.get_currency_rate_line(
                            cr, uid, st_line, currency_diff, move_id, context=context))
                else:
                    mv_line_dict['debit'] = debit_at_current_rate
                    mv_line_dict['credit'] = credit_at_current_rate
            elif statement_currency.id != company_currency.id:
                # statement is in foreign currency but the transaction is in
                # company currency
                prorata_factor = (
                    mv_line_dict['debit'] - mv_line_dict['credit']) / st_line.amount_currency
                mv_line_dict[
                    'amount_currency'] = prorata_factor * st_line.amount
            to_create.append(mv_line_dict)
        # Create move lines
        move_line_pairs_to_reconcile = []
        for mv_line_dict in to_create:
            # NB : this attribute is irrelevant for aml_obj.create() and needs
            # to be removed from the dict
            counterpart_move_line_id = None
            if mv_line_dict.get('counterpart_move_line_id'):
                counterpart_move_line_id = mv_line_dict[
                    'counterpart_move_line_id']
                del mv_line_dict['counterpart_move_line_id']
            new_aml_id = aml_obj.create(cr, uid, mv_line_dict, context=context)
            if counterpart_move_line_id is not None:
                move_line_pairs_to_reconcile.append(
                    [new_aml_id, counterpart_move_line_id])
        # Reconcile
        for pair in move_line_pairs_to_reconcile:
            aml_obj.reconcile_partial(cr, uid, pair, context=context)
        # Mark the statement line as reconciled
        self.write(cr, uid, id, {'journal_entry_id': move_id}, context=context)
