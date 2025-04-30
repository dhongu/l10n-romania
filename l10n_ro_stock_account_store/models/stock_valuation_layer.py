# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    l10n_ro_valued_type = fields.Selection(selection_add=[("in_store", "In store"), ("out_store", "Out store")])
    l10n_ro_sale_amount = fields.Float(string="Sale Amount")
