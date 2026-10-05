# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    # Same field (and column) as `l10n_ro_stock` 18.0, so the location type
    # survives the upgrade to 19.0, where `l10n_ro_stock` no longer has it.
    l10n_ro_merchandise_type = fields.Selection(
        [("store", "Store"), ("warehouse", "Warehouse")],
        string="Romania - Merchandise type",
        default="warehouse",
        help="Store: the goods in this location are kept at sale price, "
        "with the trade markup (378) and the uneligible VAT (4428).",
    )
