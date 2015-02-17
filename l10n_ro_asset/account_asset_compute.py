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

from openerp.osv import osv, fields

import time
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import calendar


class account_asset_asset(osv.osv):
    _name = 'account.asset.asset'
    _inherit = 'account.asset.asset'
    _order = 'category_id, purchase_date'

    def validate(self, cr, uid, ids, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.asset_type == 'fixed' and not asset.inventory_number:
                asset.write({'inventory_number': obj_sequence.next_by_id(
                    cr, uid, asset.category_id.sequence_id.id, context=context)})
        return super(account_asset_asset, self).validate(cr, uid, ids, context=context)

    def _compute_board_amount(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None):
        # by default amount = 0
        amount = 0
        if i == undone_dotation_number:
            amount = residual_amount
        else:
            if asset.method == 'linear':
                amount = amount_to_depr / \
                    (undone_dotation_number -
                     len(posted_depreciation_line_ids))
                if asset.prorata:
                    amount = asset.purchase_value / asset.method_number
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = round((amount_to_depr / asset.method_number) / calendar.monthrange(depreciation_date.year, depreciation_date.month)[
                                       1] * (calendar.monthrange(depreciation_date.year, depreciation_date.month)[1] - depreciation_date.day + 1), 2)
                    elif i == undone_dotation_number:
                        amount = round(
                            (amount_to_depr / asset.method_number) / total_days * (total_days - days), 2)
            elif asset.method == 'degressive':
                amount = residual_amount * asset.method_progress_factor
                if asset.prorata:
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (
                            residual_amount * asset.method_progress_factor) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (
                            residual_amount * asset.method_progress_factor) / total_days * (total_days - days)
        return amount

    def compute_depreciation_board(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        currency_obj = self.pool.get('res.currency')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.value_residual == 0.0:
                continue
            posted_lines = depreciation_lin_obj.search(cr, uid, [(
                'asset_id', '=', asset.id), ('move_check', '=', True)], order='depreciation_date desc')
            posted_depreciation_line_ids = []
            reevaluated_amount = 0.00
            for line in asset.reevaluation_ids:
                reevaluated_amount += line.diff_value
            old_posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [(
                'asset_id', '=', asset.id), ('move_check', '=', True)], order='depreciation_date desc')
            if not posted_depreciation_line_ids:
                old_depreciation_line_ids = depreciation_lin_obj.search(
                    cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
                depreciation_lin_obj.unlink(
                    cr, uid, old_depreciation_line_ids, context=context)
            else:
                old_depreciation_line_ids = depreciation_lin_obj.search(
                    cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
                if old_depreciation_line_ids:
                    depreciation_lin_obj.unlink(
                        cr, uid, old_depreciation_line_ids, context=context)
            amount_to_depr = residual_amount = asset.value_residual
            # depreciation_date = 1st January of purchase year
            purchase_date = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
            # if we already have some previous validated entries, starting date
            # isn't 1st January but last entry + method period
            if (len(posted_depreciation_line_ids) > 0):
                last_depreciation_date = datetime.strptime(depreciation_lin_obj.browse(
                    cr, uid, posted_depreciation_line_ids[0], context=context).depreciation_date, '%Y-%m-%d')
                depreciation_date = (
                    last_depreciation_date + relativedelta(months=+asset.method_period))
            else:
                if old_posted_depreciation_line_ids:
                    last_depreciation_date = datetime.strptime(depreciation_lin_obj.browse(
                        cr, uid, old_posted_depreciation_line_ids[0], context=context).depreciation_date, '%Y-%m-%d')
                    depreciation_date = (
                        last_depreciation_date + relativedelta(months=+asset.method_period))
                else:
                    depreciation_date = purchase_date
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb(
                cr, uid, asset, depreciation_date, total_days, context=context)
            residual_amount = asset.value_residual
            depr_number = undone_dotation_number
            for x in range(len(posted_depreciation_line_ids), depr_number):
                i = x + 1
                amount = self._compute_board_amount(
                    cr, uid, asset, i, residual_amount, amount_to_depr, depr_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)
                company_currency = asset.company_id.currency_id.id
                current_currency = asset.currency_id.id
                # compute amount into company currency
                amount = currency_obj.compute(
                    cr, uid, current_currency, company_currency, amount, context=context)
                if i == depr_number:
                    if residual_amount != 0:
                        vals = {
                            'amount': residual_amount,
                            'asset_id': asset.id,
                            'sequence': i,
                            'name': str(asset.id) + '/' + str(i),
                            'remaining_value': 0,
                            'depreciated_value': round((asset.purchase_value - asset.salvage_value) - residual_amount + reevaluated_amount, 2),
                            'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                        }
                        residual_amount = 0
                        depreciation_lin_obj.create(
                            cr, uid, vals, context=context)
                else:
                    residual_amount -= amount
                    vals = {
                        'amount': amount,
                        'asset_id': asset.id,
                        'sequence': i,
                        'name': str(asset.id) + '/' + str(i),
                        'remaining_value': residual_amount,
                        'depreciated_value': round((asset.purchase_value - asset.salvage_value) - (residual_amount + amount) + reevaluated_amount, 2),
                        'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                    }

                    depreciation_lin_obj.create(cr, uid, vals, context=context)
                # Considering Depr. Period as months
                depreciation_date = (
                    datetime(year, month, day) + relativedelta(months=+asset.method_period))
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
        return True
