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


class res_company(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    property_stock_usage_giving_account_id = fields.Many2one(
        'account.account', string="Usage Giving Account", domain="[('type', '=', 'other')]", help="This account will be used as the usage giving account in account move line.")
    property_undeductible_account_id = fields.Many2one(
        'account.account', string="Undeductible Account", domain="[('type', '=', 'other')]", help="This account will be used as the undeductible account for account move line.")
    property_stock_picking_payable_account_id = fields.Many2one(
        'account.account', string="Picking Account Payable", domain="[('type', '=', 'payable')]", help="This account will be used as the payable account for the current partner on stock picking notice.")
    property_stock_picking_receivable_account_id = fields.Many2one(
        'account.account', string="Picking Account Receivable", domain="[('type', '=', 'receivable')]", help="This account will be used as the receivable account for the current partner on stock picking notice.")
    property_asset_reevaluation_account_id = fields.Many2one(
        'account.account', string="Asset Reevaluation Account", domain="[('type', '=', 'other')]", help="This account will be used as the reevaluation asset account.")
    property_customer_advance_account_id = fields.Many2one(
        'account.account', string="Customer Advance Account", domain="[('type', '=', 'receivable')]", help="This account will be used as the customer advance account for the current partner on vouchers.")
    property_supplier_advance_account_id = fields.Many2one(
        'account.account', string="Supplier Advance Account", domain="[('type', '=', 'payable')]", help="This account will be used as the supplier advance account for the current partner on vouchers.")
    asset_category_chart_installed = fields.Boolean(
        'Install Chart of Asset Category')
    bank_statement_template_installed = fields.Boolean(
        'Load Bank Statement Templates')
    account_period_close_template_installed = fields.Boolean(
        'Load Account Period Close Templates')
