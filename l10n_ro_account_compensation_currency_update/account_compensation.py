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


from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
import openerp

import time
from datetime import datetime, timedelta, date


class account_compensation(osv.osv):
    _inherit = 'account.compensation'

    def _get_exchange_lines(self, cr, uid, line, move_id, amount_residual, company_currency, current_currency, context=None):
        currency_obj = self.pool.get('res.currency')
        ctx1 = context.copy()
        amount1 = round(currency_obj._get_conversion_rate(
            cr, uid, line.move_line_id.currency_id, line.move_line_id.company_id.currency_id, ctx1) * abs(line.amount), 2)
        if datetime.strptime(line.move_line_id.date, "%Y-%m-%d").month == datetime.strptime(line.compensation_id.date, "%Y-%m-%d").month:
            # get current currency rate
            date1 = datetime.strptime(line.move_line_id.date, "%Y-%m-%d")
            ctx1.update({'date': date1})
            amount2 = round(currency_obj._get_conversion_rate(
                cr, uid, line.move_line_id.currency_id, line.move_line_id.company_id.currency_id, ctx1) * abs(line.amount), 2)
            amount = round(amount1 - amount2, 2)
        else:
            ctx2 = context.copy()
            date2 = datetime.strptime(
                line.compensation_id.period_id.date_start, "%Y-%m-%d")
            ctx2.update({'date': date2})
            amount2 = round(currency_obj._get_conversion_rate(
                cr, uid, line.move_line_id.currency_id, line.move_line_id.company_id.currency_id, ctx2) * abs(line.amount), 2)
            amount = round(amount1 - amount2, 2)
        if line.account_id.type in ('receivable', 'asset'):
            amount = (-1) * amount
        return super(account_compensation, self)._get_exchange_lines(cr, uid, line, move_id, amount, company_currency, current_currency, context=context)

    def compensation_move_line_create(self, cr, uid, compensation_id, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per compensation line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param compensation_id: Compensation id what we are working with
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the compensation belong
        :param current_currency: id of currency of the compensation
        :return: Tuple build as (remaining amount not allocated on compensation lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        rec_lst_ids = super(account_compensation, self).compensation_move_line_create(
            cr, uid, compensation_id, move_id, company_currency, current_currency, context=context)
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')

        date = self.read(
            cr, uid, [compensation_id], ['date'], context=context)[0]['date']
        ctx = context.copy()
        ctx.update({'date': date})
        compensation = self.pool.get('account.compensation').browse(
            cr, uid, compensation_id, context=ctx)
        compensation_currency = compensation.journal_id.currency or compensation.company_id.currency_id
        prec = self.pool.get('decimal.precision').precision_get(
            cr, uid, 'Account')
        for line in compensation.line_ids:
            # create one move line per compensation line where amount is not 0.0
            # AND (second part of the clause) only if the original move line
            # was not having debit = credit = 0 (which is a legal value)
            rec_ids = []
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the compensation line into the currency of the compensation's company
            # this calls res_curreny.compute() with the right context, so that
            # it will take either the rate on the compensation if it is
            # relevant or will use the default behaviour
            amount = self._convert_amount(
                cr, uid, line.amount, compensation.id, context=ctx)
            # if the amount encoded in compensation is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if company_currency != current_currency:
                currency_rate_difference = 0.00
                if line.amount != line.amount_unreconciled:
                    if not line.move_line_id:
                        raise osv.except_osv(_('Wrong compensation line'), _(
                            "The invoice you are willing to pay is not valid anymore."))
                    sign = line.type == 'dr' and -1 or 1
                    currency_rate_difference = sign * amount

                if not currency_obj.is_zero(cr, uid, compensation.company_id.currency_id, currency_rate_difference):
                    # Change difference entry in company currency
                    exch_lines = self._get_exchange_lines(
                        cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                    new_id = move_line_obj.create(
                        cr, uid, exch_lines[0], context)
                    move_line_obj.create(cr, uid, exch_lines[1], context)
                    rec_ids = [new_id, line.move_line_id.id]

                if line.move_line_id.id:
                    rec_lst_ids.append(rec_ids)
        return rec_lst_ids
