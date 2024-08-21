# ©  2024 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "l10n.ro.mixin"]

    @api.model
    def _get_valued_types(self):
        valued_types = super()._get_valued_types()
        if not self.filtered("is_l10n_ro_record"):
            return valued_types

        valued_types += [
            "in_store"  # 'Intrare in magazin'
            "out_store"  # 'Iesire din maazin
        ]
        return valued_types

    def _is_in_store(self):
        """Este receptie in magazin"""
        it_is = self._is_in() and self.location_dest_id.l10n_ro_merchandise_type == "store"
        return it_is

    def _create_in_store_svl(self, forced_quantity=None):
        move = self.with_context(standard=True, valued_type="in_store")
        # inregistrarea adaosului comecial
        # 371 = %
        #       378
        #       4428
        account_diff = self.company_id.l10n_ro_property_stock_picking_payable_account_id

        svls = self.env["stock.valuation.layer"]
        # move._create_account_move_line(
        #     acc_dest,
        #     acc_valuation,
        #     journal_id,
        #     qty,
        #     description,
        #     svl_id,
        #     qty * sale_price,
        # )
        svl_vals_list = []
        for move_line in move.move_line_ids:
            if move_line.qty_done == 0:
                continue
            svl_vals = {}
            svl_vals.update(move._prepare_common_svl_vals())
            svl_vals_list.append(svl_vals)
        return self.env["stock.valuation.layer"].sudo().create(svl_vals_list)

    def _is_out_store(self):
        """Este iesire din magazin"""
        it_is = self._is_out() and self.location_id.l10n_ro_merchandise_type == "store"
        return it_is

    def _create_out_store_svl(self, forced_quantity=None):
        #       % = 371
        #     607
        #     378
        #     4428

        move = self.with_context(standard=True, valued_type="out_store")
        svl_vals_list = []
        for move_line in move.move_line_ids:
            if move_line.qty_done == 0:
                continue
            svl_vals = {}
            svl_vals.update(move._prepare_common_svl_vals())
            svl_vals_list.append(svl_vals)
        return self.env["stock.valuation.layer"].sudo().create(svl_vals_list)
