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


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def _create_correction_svl(self, move, diff):
        super(StockMoveLine, self)._create_correction_svl(move, diff)
        if not self.company_id.romanian_accounting:
            return

        stock_valuation_layers = self.env["stock.valuation.layer"]

        for valued_type in move._get_valued_types():
            if getattr(move, "_is_%s" % valued_type)():

                if diff < 0 and "_return" not in valued_type:
                    valued_type = valued_type + "_return"
                if diff > 0 and "_return" in valued_type:
                    valued_type = valued_type.replace("_return", "")

                if valued_type == "plus_inventory_return":
                    valued_type = "minus_inventory"
                elif valued_type == "minus_inventory_return":
                    valued_type = "plus_inventory"
                elif valued_type == "internal_transfer_return":
                    valued_type = "internal_transfer"

                if hasattr(move, "_create_%s_svl" % valued_type):
                    stock_valuation_layers |= getattr(move, "_create_%s_svl" % valued_type)(forced_quantity=abs(diff))

        for svl in stock_valuation_layers:
            if not svl.product_id.valuation == "real_time":
                continue
            svl.stock_move_id._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)
