# ©  2015-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def correction_valuation(self):
        for move in self:
            # move.product_price_update_before_done()
            for svl in move.stock_valuation_layer_ids:
                svl.account_move_id.write({"state": "draft"})
                svl.account_move_id.with_context(force_delete=True).unlink()
                stock_move = svl.stock_move_id.with_context(force_period_date=move.date)
                stock_move._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)



