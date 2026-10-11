# Copyright (C) 2014 Forest and Biomass Romania
# Copyright (C) 2020 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

MOVE_TYPE = [
    ("reception", "Reception"),
    ("reception_return", "Reception Return"),
    ("reception_notice", "Reception Notice"),
    ("reception_notice_return", "Reception Notice Return"),
    ("reception_in_progress", "Reception In Progress"),
    ("reception_in_progress_return", "Reception In Progress Return"),
    ("delivery", "Delivery"),
    ("delivery_return", "Delivery Return"),
    ("delivery_notice", "Delivery Notice"),
    ("delivery_notice_return", "Delivery Notice Return"),
    ("plus_inventory", "Plus Inventory"),
    ("minus_inventory", "Minus Inventory"),
    ("consumption", "Consumption"),
    ("consumption_return", "Consumption Return"),
    ("usage_giving", "Usage Giving"),
    ("usage_giving_return", "Usage Giving Return"),
    ("production", "Production"),
    ("production_return", "Production Return"),
    ("internal_transfer", "Internal Transfer"),
    ("internal_transit_out", "Internal Transit Out"),
    ("internal_transit_in", "Internal Transit In"),
    ("dropshipped", "Dropshipped"),
    ("dropshipped_return", "Dropshipped Return"),
]


class StockMove(models.Model):
    _inherit = "stock.move"

    l10n_ro_extra_account_move_ids = fields.One2many(
        "account.move",
        "l10n_ro_extra_stock_move_id",
        string="Romania - Extra Account Moves",
        readonly=True,
        copy=False,
    )
    l10n_ro_move_type = fields.Selection(
        MOVE_TYPE,
        string="Romanian - Move Type",
        help="Specify the type of stock move for Romanian localization.",
    )
    l10n_ro_account_id = fields.Many2one(
        "account.account",
        string="Romania - Valuation Account",
    )
    l10n_ro_transfer_account_id = fields.Many2one(
        "account.account",
        string="Romania - Transfer Valuation Account",
    )

    _fifo_neg_pending_idx = models.Index(
        "(product_id, location_id, company_id, date, id) "
        "WHERE fifo_neg_pending_qty > 0 AND state = 'done'"
    )

    fifo_neg_pending_qty = fields.Float(
        string="Negative Stock Pending Qty",
        copy=False,
        readonly=True,
        help="Quantity from a FIFO outgoing move that was valued at "
        "standard_price because the location stack was empty.",
    )
    fifo_neg_origin_value = fields.Monetary(
        string="Negative Stock Initial Value",
        currency_field="company_currency_id",
        copy=False,
        readonly=True,
    )
    fifo_neg_compensation_move_ids = fields.One2many(
        "account.move",
        "fifo_neg_origin_move_id",
        string="Negative Stock Compensation Entries",
        readonly=True,
    )
