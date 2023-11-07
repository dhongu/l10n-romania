# ©  2023 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models

# from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def action_apply_inventory(self):
        super().action_apply_inventory()
        # self.check_valuation_layer()

    # def check_valuation_layer(self):
    #     for quant in self:
    #         # se determina cantitatea din lot
    #         quant_qty = quant.quantity
    #
    #         # se determina cantitatea din svl
    #
    #         product = quant.product_id.with_context(lot_id=quant.lot_id, location_id=quant.location_id)
    #         svl_qty = product.svl_qty
