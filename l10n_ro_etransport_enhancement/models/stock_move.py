# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends("name", "product_id.display_name", "picking_id.name")
    def _compute_display_name(self):
        # First compute the standard display_name
        super()._compute_display_name()

        # Allow opting out via context if needed
        if not self.env.context.get("show_product_in_move", False):
            return

        for move in self:
            product_label = move.product_id.with_context(display_default_code=True).display_name or "-"
            picking_label = move.picking_id.name or ""
            original = move.name or ""

            parts = [product_label]
            if picking_label:
                parts.append(picking_label)
            # Only add the original name if it’s different/useful
            if original and original not in parts:
                parts.append(original)

            move.display_name = " - ".join(parts)
