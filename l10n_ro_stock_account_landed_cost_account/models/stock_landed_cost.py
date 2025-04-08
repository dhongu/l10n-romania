# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    def _create_account_move_line(self, move, credit_account_id, debit_account_id, qty_out, already_out_account_id):
        stock_move = self.move_id

        location_from = stock_move.location_id
        location_to = stock_move.location_dest_id
        from_account = location_from.l10n_ro_property_stock_valuation_account_id
        to_account = location_to.l10n_ro_property_stock_valuation_account_id

        if stock_move._is_in():
            debit_account_id = to_account.id or debit_account_id

        if stock_move._is_out():
            debit_account_id = from_account.id or debit_account_id

        accounts = self.product_id.product_tmpl_id.get_product_accounts()
        already_out_account_id = accounts.get('expense') and accounts['expense'].id or False

        fiscal_position = self.cost_id.account_journal_id.l10n_ro_fiscal_position_id
        if fiscal_position:
            credit_account_id = fiscal_position.map_account(credit_account_id)
            debit_account_id = fiscal_position.map_account(debit_account_id)
            already_out_account_id = fiscal_position.map_account(already_out_account_id)

        return super()._create_account_move_line(
            move, credit_account_id, debit_account_id, qty_out, already_out_account_id
        )
