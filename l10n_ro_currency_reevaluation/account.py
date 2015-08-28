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
import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp


class account_account(models.Model):
    _inherit = "account.account"

    currency_reevaluation = fields.Boolean("Allow Currency reevaluation")

class account_move_line(models.Model):
    _inherit = "account.move.line"

    currency_reevaluation = fields.Boolean("Currency reevaluation")

from openerp.osv import osv, fields

class account_move_line(osv.Model):
    _inherit = "account.move.line"
    
    # Rewrite residual function to allow amount residual according to storno
    # journals.
    def _amount_residual(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        if context is None:
            context = {}
        res = {}
        if context is None:
            context = {}
        cur_obj = self.pool.get('res.currency')
        for move_line in self.browse(cr, uid, ids, context=context):
            res[move_line.id] = {
                'amount_residual': 0.0,
                'amount_residual_currency': 0.0,
            }

            if move_line.reconcile_id:
                continue
            if not move_line.account_id.reconcile:
                # this function does not suport to be used on move lines not
                # related to a reconcilable account
                continue

            if move_line.currency_id:
                move_line_total = move_line.amount_currency
                sign = move_line.amount_currency < 0 and -1 or 1
            else:
                move_line_total = move_line.debit - move_line.credit
                sign = (move_line.debit - move_line.credit) < 0 and -1 or 1
            line_total_in_company_currency = move_line.debit - move_line.credit
            context_unreconciled = context.copy()
            if move_line.reconcile_partial_id:
                for payment_line in move_line.reconcile_partial_id.line_partial_ids:
                    if payment_line.id == move_line.id:
                        continue
                    if payment_line.currency_id and move_line.currency_id and payment_line.currency_id.id == move_line.currency_id.id:
                        move_line_total += payment_line.amount_currency
                    else:
                        if not payment_line.currency_reevaluation:
                            if move_line.currency_id:
                                context_unreconciled.update(
                                    {'date': payment_line.date})
                                amount_in_foreign_currency = cur_obj.compute(
                                    cr,
                                    uid,
                                    move_line.company_id.currency_id.id,
                                    move_line.currency_id.id,
                                    (payment_line.debit - payment_line.credit),
                                    round=False,
                                    context=context_unreconciled)
                                move_line_total += amount_in_foreign_currency
                            else:
                                move_line_total += (payment_line.debit -
                                                payment_line.credit)
                    line_total_in_company_currency += (
                        payment_line.debit - payment_line.credit)

            result = move_line_total
            res[
                move_line.id]['amount_residual_currency'] = sign * (
                move_line.currency_id and self.pool.get('res.currency').round(
                    cr,
                    uid,
                    move_line.currency_id,
                    result) or result)
            res[move_line.id]['amount_residual'] = sign * \
                line_total_in_company_currency
            if move_line.journal_id.posting_policy == 'storno':
                if move_line.debit < 0 or move_line.credit < 0:
                    res[move_line.id]['amount_residual_currency'] = res[
                        move_line.id]['amount_residual_currency'] * (-1)
                    res[move_line.id]['amount_residual'] = res[
                        move_line.id]['amount_residual'] * (-1)
        return res

    _columns = {
        'amount_residual_currency': fields.function(
            _amount_residual,
            string='Residual Amount in Currency',
            multi="residual",
            help="The residual amount on a receivable or payable of a journal entry expressed in its currency (maybe different of the company currency)."),
        'amount_residual': fields.function(
            _amount_residual,
            string='Residual Amount',
            multi="residual",
            help="The residual amount on a receivable or payable of a journal entry expressed in the company currency."),
    }
