# ©  2008-2019 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        # În 20.0 `purchase.order._prepare_picking` a fost eliminat: recepția se creează
        # din mișcări (`stock.move._assign_picking`). Păstrăm comportamentul din 19.0:
        # documentul de origine al recepției e numărul documentului furnizorului
        # (`partner_ref`), altfel originea comenzii — cel tipărit pe NIR.
        vals = super()._get_new_picking_values()
        order = self.purchase_line_id.order_id
        if len(order) == 1:
            vals["origin"] = order.partner_ref or order.origin
        return vals
