# Copyright (C) 2021 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    date = fields.Datetime(related="stock_move_id.date")
    rounding_adjustment = fields.Char("Rounding Adjustment")

    def correction_valuation(self):
        val_types = self.env["stock.move"]._get_valued_types()
        val_types = [val for val in val_types if val not in ["in", "out", "dropshipped", "dropshipped_returned"]]

        for svl in self:
            if not svl.stock_move_id:
                continue

            for valued_type in val_types:
                if getattr(svl.stock_move_id, "_is_%s" % valued_type)():
                    svl.valued_type = valued_type
                    continue

            if svl.valued_type == 'delivery':
                product = svl.product_id
                if svl.stock_move_id.lot_ids:
                    product = svl.product_id.with_context(lot_ids=svl.stock_move_id.lot_ids)
                svsl_vals = product._prepare_out_svl_vals(abs(svl.quantity), svl.company_id)
                svl.write({
                    'unit_cost': svsl_vals['unit_cost'],
                    'value':  svsl_vals['unit_cost'] * svl.quantity
                })

            svl.account_move_id.write({"state": "draft"})
            name = svl.account_move_id.name
            svl.account_move_id.with_context(force_delete=True).unlink()
            stock_move = svl.stock_move_id.with_context(force_period_date=svl.stock_move_id.date)
            stock_move._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)
            if name and svl.account_move_id:
                svl.account_move_id.write({"name": name})
