# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends_context("show_product_in_move")
    def _compute_display_name(self):
        super()._compute_display_name()
        if not self.env.context.get("show_product_in_move"):
            return
        for move in self.filtered("product_id"):
            move.display_name = move.product_id.display_name
