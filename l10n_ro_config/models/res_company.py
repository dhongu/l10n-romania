##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu@gmail.com>
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

from odoo import _, api, fields, models

import odoo.addons.decimal_precision as dp


class res_company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    share_capital = fields.Float(string="Share Capital", digits=dp.get_precision("Account"), default=200)
    stamp_image = fields.Binary(string="Stamp image")

    property_stock_usage_giving_account_id = fields.Many2one(
        "account.account",
        string="Usage Giving Account",
        domain="[('internal_type', '=', 'other')]",
        help="This account will be used as the usage giving account in account move line.",
    )
    property_undeductible_account_id = fields.Many2one(
        "account.account",
        string="Undeductible Account",
        domain="[('internal_type', '=', 'other')]",
        help="This account will be used as the undeductible expense account for account move line.",
    )
    property_undeductible_tax_account_id = fields.Many2one(
        "account.account",
        string="Undeductible Tax Account",
        domain="[('internal_type', '=', 'other')]",
        help="This account will be used as the undeductible tax account for account move line.",
    )
    property_stock_picking_payable_account_id = fields.Many2one(
        "account.account",
        string="Picking Account Payable",
        domain="[('internal_type', 'in', ['payable','other'])]",
        help="This account will be used as the payable account for the current partner on stock picking notice.",
    )
    property_stock_picking_receivable_account_id = fields.Many2one(
        "account.account",
        string="Picking Account Receivable",
        domain="[('internal_type', 'in', ['receivable','other'])]",
        help="This account will be used as the receivable account for the current partner on stock picking notice.",
    )
    property_stock_picking_custody_account_id = fields.Many2one(
        "account.account",
        string="Picking Account Custody",
        help="This account will be used as the extra trial balance payable account for the current partner on stock picking received in custody.",
    )
    property_asset_reevaluation_account_id = fields.Many2one(
        "account.account",
        string="Asset Reevaluation Account",
        domain="[('internal_type', '=', 'other')]",
        help="This account will be used as the reevaluation asset account.",
    )
    property_customer_advance_account_id = fields.Many2one(
        "account.account",
        string="Customer Advance Account",
        domain="[('internal_type', 'in', ['receivable','other'])]",
        help="This account will be used as the customer advance account for the current partner on vouchers.",
    )
    property_supplier_advance_account_id = fields.Many2one(
        "account.account",
        string="Supplier Advance Account",
        domain="[('internal_type', 'in', ['payable','other'])]",
        help="This account will be used as the supplier advance account for the current partner on vouchers.",
    )

    property_stock_transfer_account_id = fields.Many2one("account.account", string="Stock Transfer Account")

    property_trade_discount_received_account_id = fields.Many2one("account.account", string="Trade discounts received")
    property_trade_discount_granted_account_id = fields.Many2one("account.account", string="Trade discounts granted")

    property_vat_on_payment_position_id = fields.Many2one("account.fiscal.position", "VAT on Payment")
    property_inverse_taxation_position_id = fields.Many2one("account.fiscal.position", "Inverse Taxation")
