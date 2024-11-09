# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    l10n_ro_valued_type = fields.Selection(
        selection_add=[("reception_store", "Reception in store"), ("delivery_store", "Delivery from store")]
    )
