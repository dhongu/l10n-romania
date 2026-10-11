# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    fifo_per_location = fields.Boolean(
        string="FIFO per Location",
        help="Enable FIFO valuation at the source location level (instead "
        "of the company level).",
    )
    fifo_location_negative_compensation = fields.Boolean(
        string="FIFO Negative Stock Compensation",
        help="Compensate the negative stock of the FIFO outgoing moves on the "
        "next incoming move.",
    )
    l10n_ro_property_stock_picking_payable_account_id = fields.Many2one(
        "account.account",
        string="Romania - Picking Account Payable",
        domain="[('account_type', 'in', ['liability_current','income_other'])]",
        help="This account will be used as the payable account for the "
        "current partner on stock picking notice.",
    )
    l10n_ro_property_stock_picking_receivable_account_id = fields.Many2one(
        "account.account",
        string="Romania - Picking Account Receivable",
        domain="[('account_type', 'in', ['asset_current','income_other'])]",
        help="This account will be used as the receivable account for the "
        "current partner on stock picking notice.",
    )
    l10n_ro_property_stock_usage_giving_account_id = fields.Many2one(
        "account.account",
        string="Romania - Usage Giving Account",
        domain="[('account_type', '=', 'income_other')]",
        help="This account will be used as the usage giving "
        "account in account move line.",
    )
    l10n_ro_property_stock_transfer_account_id = fields.Many2one(
        "account.account",
        string="Romania - Company Stock Transfer Account",
        domain="[('account_type', '=', 'liability_current')]",
        help="This account will be used as an intermediary account for "
        "account move line generated from internal moves between company "
        "stores.",
    )
    l10n_ro_property_uneligible_tax_account_id = fields.Many2one(
        "account.account",
        string="Romania - Not Eligible Tax Account",
        domain="[('account_type', 'in', ['liability_non_current','income_other'])]",
        help="This account will be used as the not eligible tax account for "
        "account move line.\nUsed in especially in inventory losses.",
    )
