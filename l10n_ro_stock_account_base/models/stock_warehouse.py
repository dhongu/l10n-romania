# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    l10n_ro_fiscal_position_id = fields.Many2one(
        "account.fiscal.position", string="Fiscal Position"
    )
