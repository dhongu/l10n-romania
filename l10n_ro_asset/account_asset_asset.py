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
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp

import time
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import calendar


class account_asset_category(models.Model):
    _name = 'account.asset.category'
    _inherit = 'account.asset.category'

    # Redefine accounting properties to be required for asset category type
    # 'Normal', specified in view
    account_asset_id = fields.Many2one('account.account', 'Category Asset Account',
                                       required=False, domain="[('type','=','other'),('company_id','=',company_id)]")
    account_depreciation_id = fields.Many2one(
        'account.account', 'Depreciation Account', domain="[('type','=','other'),('company_id','=',company_id)]", required=False)
    account_expense_depreciation_id = fields.Many2one(
        'account.account', 'Depr. Expense Account', domain="[('type','=','other'),('company_id','=',company_id)]", required=False)
    journal_id = fields.Many2one(
        'account.journal', 'Journal', required=False, domain="[('company_id','=',company_id)]")
    prorata = fields.Boolean(
        'Prorata Temporis', help='Indicates that the first depreciation entry for this asset have to be done from the purchase date instead of first day of next month.')
    # Redefine depreciation properties to be required for asset category type
    # 'Normal'
    method = fields.Selection([('linear', 'Linear'), ('degressive', 'Degressive')], 'Computation Method', help="Choose the method to use to compute the amount of depreciation lines.\n"
                              "  * Linear: Calculated on basis of: Gross Value / Number of Depreciations\n"
                              "  * Degressive: Calculated on basis of: Residual Value * Degressive Factor", required=False)
    method_period = fields.Integer(
        'Period Length', help="State here the time between 2 depreciations, in months", required=False)
    method_time = fields.Selection([('number', 'Number of Depreciations'), ('end', 'Ending Date')], 'Time Method',
                                   help="Choose the method to use to compute the dates and number of depreciation lines.\n"
                                   "  * Number of Depreciations: Fix the number of depreciation lines and the time between 2 depreciations.\n"
                                   "  * Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond.", required=False)
    account_income_id = fields.Many2one('account.account', string='Income Account',
                                        domain="[('type','=','other'),('company_id','=',company_id)]", required=False)
    code = fields.Char(string='Code', index=True, required=True)
    type = fields.Selection(
        [('view', 'View'), ('normal', 'Normal')], string='Category Type', required=True)
    asset_type = fields.Selection(
        [('none', 'None'), ('fixed', 'Fixed Assets'), ('service', 'Services Assets')], string='Asset Type')
    method_number_min = fields.Integer(
        'Minimum Number of Depreciations', help="The minimum number of depreciations of your asset - expressed in months")
    method_number = fields.Integer('Maximum Number of Depreciations', help="The maximum number of depreciations of your asset (taken by default) \
        - expressed in months")
    parent_id = fields.Many2one('account.asset.category', 'Parent Category')
    child_ids = fields.One2many(
        'account.asset.category', 'parent_id', 'Children Categories', copy=True, readonly=True)
    sequence_id = fields.Many2one('ir.sequence', 'Inventory Sequence', help="This field contains the information related to the inventory numbering \
       of the assets from this category.", copy=False)

    # @api.one
    # @api.constrains('parent_id')
    # def _check_recursion(self, parent=None):
    #    if self._check_recursion(parent=self.parent_id):
    #        raise Warning(_('Error ! You cannot create recursive asset categories.'))


class account_asset_asset(models.Model):
    _name = 'account.asset.asset'
    _inherit = 'account.asset.asset'
    _order = 'category_id, purchase_date'

    @api.one
    def sale_close_asset(self, move):
        depr_lines_obj = self.env['account.asset.depreciation.line']
        depr_line = depr_lines_obj.search(
            [('asset_id', '=', self.id), ('move_check', '=', False)])
        if depr_line:
            depr_line[0].write(
                {'amount': self.value_residual, 'remaining_value': 0.00, 'depreciation_date': move.date})
            depr_line[0].create_move()
            self.compute_depreciation_board()
        return True

    @api.one
    def _get_depreciated_value(self):
        self.value_depreciated = self.purchase_value - self.value_residual

    @api.one
    def _get_monthly_depreciation(self):
        self.amount_depreciation = self.value_residual / self.method_number

    @api.one
    def _amount_residual(self):
        self._cr.execute("""SELECT
                l.asset_id as id, sum(l.debit-l.credit) AS amount
            FROM
                account_move_line l
            WHERE
                l.asset_id = %s GROUP BY l.asset_id """, (self.id,))
        res = dict(self._cr.fetchall())
        self.value_residual = self.purchase_value + \
            res.get(self.id, 0.0) - self.salvage_value

    category_id = fields.Many2one('account.asset.category', 'Asset Category', required=True, change_default=True, readonly=True, states={
                                  'draft': [('readonly', False)]}, domain="[('type','=','normal'),'|',('company_id','=',False),('company_id','=',user.company_id)]")
    purchase_date = fields.Date('Depreciation Start Date', required=True, readonly=True, states={
                                'draft': [('readonly', False)]})
    prorata = fields.Boolean('Prorata Temporis', readonly=True, states={'draft': [(
        'readonly', False)]}, help='Indicates that the first depreciation entry for this asset have to be done from the purchase date instead of first day of next month')
    product_id = fields.Many2one('product.product', string='Product',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    asset_type = fields.Selection([('fixed', 'Fixed Assets'), ('service', 'Services Assets')],
                                  related='category_id.asset_type', string='Asset Type', readonly=True, store=True)
    entry_date = fields.Date(
        'Purchase Date', readonly=True, states={'draft': [('readonly', False)]})
    value_residual = fields.Float(
        'Residual Value', readonly=True, compute='_amount_residual')
    value_depreciated = fields.Float(
        'Depreciated Value', readonly=True, compute='_get_depreciated_value')
    amount_depreciation = fields.Float(
        'Monthly Depreciation', readonly=True, compute='_get_monthly_depreciation')
    reevaluation_ids = fields.One2many(
        'account.asset.reevaluation', 'asset_id', 'Reevaluations', copy=True)

    @api.one
    @api.constrains('method_number')
    def _check_method_number(self):
        if (self.method_time == 'number') and ((self.method_number < self.category_id.method_number_min) or (self.method_number > self.category_id.method_number)):
            raise Warning(
                _('Number of depreciations invalid, it must be between asset category limits.'))


class account_asset_reevaluation(models.Model):
    _name = 'account.asset.reevaluation'
    _description = "Asset Reevaluation"
    _order = "date"

    @api.one
    @api.depends('move_id')
    def _get_move_check(self):
        self.move_check = bool(self.move_id)

    @api.one
    @api.depends('new_value', 'value_residual')
    def _get_diff_value(self):
        self.diff_value = self.new_value - self.value_residual

    type = fields.Selection([('reevaluation', 'Reevaluation'), ('modernization', 'Modernization'), ('cassation', 'Cassation')],
                            string='Reevaluation Type', required=True, readonly=True, states={'draft': [('readonly', False)]}, store=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             string='Reevaluation State', required=True, store=True, default='draft')
    date = fields.Date('Reevaluation Date', readonly=True, states={
                       'draft': [('readonly', False)]}, default=time.strftime('%Y-%m-%d'))
    asset_id = fields.Many2one('account.asset.asset', required=True,
                               change_default=True, readonly=True, states={'draft': [('readonly', False)]})
    value_residual = fields.Float(
        'Asset Value', related='asset_id.value_residual', readonly=True, store=True)
    new_value = fields.Float('New Asset Value', required=True, readonly=True, states={
                             'draft': [('readonly', False)]})
    diff_value = fields.Float(
        'Reevaluation Difference', readonly=True, compute='_get_diff_value', store=True)
    move_id = fields.Many2one(
        'account.move', 'Depreciation Entry', readonly=True)
    move_check = fields.Boolean(
        compute='_get_move_check', string='Posted', store=True, track_visibility='always')

    @api.one
    def create_move(self):
        context = dict(self._context)
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        move_date = self.date
        period_id = period_obj.find(move_date)[:1]
        context.update({'date': move_date})
        amount = self.diff_value
        asset_name = self.asset_id.name
        reference = 'Reevaluation asset ' + asset_name
        if not self.asset_id.company_id.property_asset_reevaluation_account_id:
            raise Warning(
                _('You need to configure the Asset Reevaluation Account in the Romanian Accounting Page of your company.'))
        move_vals = {
            'name': 'Reevaluation asset ' + asset_name,
            'date': move_date,
            'ref': reference,
            'period_id': period_id and period_id.id or False,
            'journal_id': self.asset_id.category_id.journal_id.id,
        }
        move_id = move_obj.create(move_vals)
        journal_id = self.asset_id.category_id.journal_id.id
        partner_id = self.asset_id.partner_id.id

        move_line_obj.create({
            'name': asset_name,
            'ref': reference,
            'move_id': move_id[0].id,
            'account_id': amount > 0 and self.asset_id.company_id.property_asset_reevaluation_account_id.id or self.asset_id.category_id.account_asset_id.id,
            'debit': 0.0,
            'credit': abs(amount),
            'partner_id': partner_id,
            'asset_id': amount < 0 and self.asset_id.id or False
        })
        move_line_obj.create({
            'name': asset_name,
            'ref': reference,
            'move_id': move_id[0].id,
            'account_id': amount < 0 and self.asset_id.company_id.property_asset_reevaluation_account_id.id or self.asset_id.category_id.account_asset_id.id,
            'credit': 0.0,
            'debit': abs(amount),
            'partner_id': partner_id,
            'asset_id': amount > 0 and self.asset_id.id or False
        })
        self.write({'move_id': move_id[0].id})
        self.asset_id.compute_depreciation_board()
        return True
