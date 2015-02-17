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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api

# ----------------------------------------------------------
# Stock Move
# ----------------------------------------------------------


class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move, self)._get_invoice_line_vals(
            cr, uid, move, partner, inv_type, context=context)
        fp_obj = self.pool.get('account.fiscal.position')

        # For asset reception use the asset account available in asset
        # category.
        account_id = res['account_id']
        if inv_type in ('in_invoice', 'in_refund'):
            if move.asset_category_id:
                account_id = move.asset_category_id.account_asset_id and move.asset_category_id.account_asset_id.id
        # For asset delivery use the asset income account available in asset
        # category.
        else:
            if move.asset_id and move.asset_id.category_id:
                account_id = move.asset_id.category_id.account_income_id and move.asset_id.category_id.account_income_id.id
        fiscal_position = partner.property_account_position
        account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        res['account_id'] = account_id
        return res

# ----------------------------------------------------------
# Stock Quant
# ----------------------------------------------------------


class stock_quant(osv.osv):
    _name = "stock.quant"
    _inherit = "stock.quant"

    def _account_entry_move(self, cr, uid, quants, move, context=None):
        """
        Accounting Valuation Entries

        quants: browse record list of Quants to create accounting valuation entries for. Unempty and all quants are supposed to have the same location id (thay already moved in)
        move: Move to use. browse record
        """
        if context is None:
            context = {}
        location_obj = self.pool.get('stock.location')
        location_from = move.location_id
        location_to = quants[0].location_id
        company_from = location_obj._location_owner(
            cr, uid, location_from, context=context)
        company_to = location_obj._location_owner(
            cr, uid, location_to, context=context)

        if move.product_id.valuation != 'real_time':
            return False
        for q in quants:
            if q.owner_id:
                # if the quant isn't owned by the company, we don't make any
                # valuation entry
                return False
            if q.qty <= 0:
                # we don't make any stock valuation for negative quants because the valuation is already made for the counterpart.
                # At that time the valuation will be made at the product cost price and afterward there will be new accounting entries
                # to make the adjustments when we know the real cost price.
                return False

        # in case of routes making the link between several warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        # Create Journal Entry for stock moves
        ctx = context.copy()
        if company_to and move.location_id.usage in ('supplier', 'customer'):
            ctx['force_company'] = company_to.id
        if company_from and move.location_dest_id.usage in ('supplier', 'customer'):
            ctx['force_company'] = company_from.id

        # Put notice in context if the picking is a notice
        ctx['notice'] = move.picking_id and move.picking_id.notice

        # Create account moves for asset stock moves
        if move.location_asset or move.location_dest_asset:
            res = {}
            # Change context to create account moves for asset reception on
            # notice  (e.g. 418 = 21xx)
            if move.location_dest_asset:
                ctx['type'] = 'asset_reception'
            # Change context to create account moves for cost of goods sold
            # (e.g. 681 = 21xx)
            if move.location_asset:
                ctx['type'] = 'asset_delivery'
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(
                cr, uid, move, context=ctx)
            if acc_src and acc_dest and acc_src != acc_dest:
                res = self._create_account_move_line(
                    cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)
            if move.location_asset:
                if move.asset_id:
                    move.asset_id.sale_close_asset(move)
            return res
        return super(stock_quant, self)._account_entry_move(cr, uid, quants, move, context=ctx)

    def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
        res = super(stock_quant, self)._prepare_account_move_line(
            cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
        debit_line_vals = res[0][2]
        credit_line_vals = res[1][2]
        if context is None:
            context = {}
        asset_obj = self.pool.get('account.asset.asset')

        # Calculate VAT base and amount for price differences and associate it
        # to account move lines
        if context.get('type', False) and context['type'] in ('asset_delivery'):
            if move.asset_id:
                last_depr_date = asset_obj._get_last_depreciation_date(
                    cr, uid, [move.asset_id.id])
                if last_depr_date:
                    depr_date = (datetime.strptime(
                        last_depr_date[move.asset_id.id], "%Y-%m-%d") + relativedelta(day=1)).date()
                    move_date = (
                        datetime.strptime(move.date[:10], "%Y-%m-%d") + relativedelta(day=1)).date()
                    if move.date == depr_date:
                        if context['type'] == 'asset_delivery':
                            valuation_amount = move.asset_id.purchase_value - \
                                move.asset_id.value_residual
                            debit_line_vals['debit'] = valuation_amount
                            debit_line_vals['credit'] = 0.00
                            credit_line_vals['credit'] = valuation_amount
                            credit_line_vals['debit'] = 0.00
                    elif move_date > depr_date:
                        raise osv.except_osv(_('Error!'), _("You cannot sell this asset ' %s ' because it hasn't been depreciated up to date. \
                           Please depreciate the asset inclusive the current month. " % move.asset_id.name))
                    elif move_date < depr_date:
                        raise osv.except_osv(_('Error!'), _(
                            "You cannot sell this asset ' %s ' because it has been depreciated in advance." % move.asset_id.name))

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        """
        Return the accounts and journal to use to post Journal Entries for the real-time
        valuation of the quant.

        :param context: context dictionary that can explicitly mention the company to consider via the 'force_company' key
        :returns: journal_id, source account, destination account, valuation account
        :raise: osv.except_osv() is any mandatory account or journal is not defined.
        """
        if context is None:
            context = {}
        journal_id, acc_src, acc_dest, acc_valuation = super(
            stock_quant, self)._get_accounting_data_for_valuation(cr, uid, move, context=context)

        # Change accounts to suit romanian assets stock account moves.
        if context.get('type', False):
            move_type = context.get('type')
            if move_type == 'asset_reception':
                # Change the account to the asset one (21xx) to suit move 418 =
                # 21xx in case it is a incoming notice
                acc_dest = move.asset_category_id.account_asset_id and move.asset_category_id.account_asset_id.id or False
                if move and move.picking_id and not move.picking_id.notice:
                    acc_src = False
            elif move_type == 'asset_delivery':
                # Change the account to the depreciation expense one (6xx) to
                # suit move: 68xx = 21xx
                acc_src = move.asset_id.category_id.account_asset_id and move.asset_id.category_id.account_asset_id.id or False
                acc_dest = move.asset_id.category_id.account_expense_depreciation_id and move.asset_id.category_id.account_expense_depreciation_id.id or False
        return journal_id, acc_src, acc_dest, acc_valuation
