# ©  2015-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

from odoo import fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def correction_valuation(self):
        for move in self:
            # move.product_price_update_before_done()
            if not move.stock_valuation_layer_ids:
                move.correction_create_svl()
            for svl in move.stock_valuation_layer_ids:
                svl.account_move_id.write({"state": "draft"})
                svl.account_move_id.with_context(force_delete=True).unlink()
                stock_move = svl.stock_move_id.with_context(force_period_date=move.date)
                stock_move._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)

    def correction_create_svl(self):
        val_types = self.env["stock.move"]._get_valued_types()
        val_types = [val for val in val_types if val not in ["in", "out", "dropshipped", "dropshipped_returned"]]

        valued_moves = {valued_type: self.env["stock.move"] for valued_type in val_types}

        for move in self.with_context(tracking_disable=True):
            move = move.with_context(force_period_date=move.date)

            if move.stock_valuation_layer_ids:
                continue
            if move.state != "done":
                continue
            if float_is_zero(move.quantity_done, precision_rounding=move.product_uom.rounding):
                continue
            for valued_type in val_types:
                if getattr(move, "_is_%s" % valued_type)():
                    valued_moves[valued_type] |= move
                    continue

        stock_valuation_layers = self.env["stock.valuation.layer"].sudo()
        # Create the valuation layers in batch by calling `moves._create_valued_type_svl`.
        for valued_type in val_types:
            todo_valued_moves = valued_moves[valued_type]
            for move in todo_valued_moves:
                move = move.with_context(force_period_date=move.date, use_move_price_unit=True, move=move)
                stock_valuation_layers |= getattr(move, "_create_%s_svl" % valued_type)()

        for svl in stock_valuation_layers.with_context(active_test=False):
            if not svl.product_id.valuation == "real_time":
                continue
            if svl.currency_id.is_zero(svl.value):
                continue
            move = svl.stock_move_id.with_context(force_period_date=svl.stock_move_id.date)
            move._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)

    def correction_recreate_svl(self):
        for move in self:
            for svl in move.stock_valuation_layer_ids:
                svl.account_move_id.write({"state": "draft", "name": "/"})
                svl.account_move_id.line_ids.unlink()
                svl.account_move_id.with_context(force_delete=True).unlink()

            move.stock_valuation_layer_ids.unlink()

            if not move.stock_valuation_layer_ids and move.state == "done":
                move.correction_create_svl()

    def _get_price_unit_from_svl(self):
        move = self
        # calculez valoarea de stoc din momentul documentului
        query = """

                SELECT
                    COALESCE(sum(svl.value), 0)  as amount,
                    COALESCE(sum(svl.quantity), 0)  as quantity

                from product_product as prod
                left join stock_move as sm ON sm.product_id = prod.id AND sm.state = 'done' AND
                    sm.company_id = %(company)s AND
                     sm.date <  %(date)s AND
                    (sm.location_id = %(location)s OR sm.location_dest_id = %(location)s)
                left join stock_valuation_layer as svl on svl.stock_move_id = sm.id and
                        ((valued_type !='internal_transfer' or valued_type is Null) or
                         (valued_type ='internal_transfer' and quantity<0 and
                          sm.location_id = %(location)s) or
                         (valued_type ='internal_transfer' and quantity>0 and
                          sm.location_dest_id = %(location)s))
                where prod.id = %(product)s

        """
        params = {
            "location": move.location_id.id,
            "product": move.product_id.id,
            "company": move.company_id.id,
            "date": fields.Datetime.to_string(move.date),
        }

        self.env.cr.execute(query, params=params)
        res = self.env.cr.dictfetchone()
        price = move.product_id.standard_price
        if res["quantity"]:
            price = res["amount"] / res["quantity"]

        return price
