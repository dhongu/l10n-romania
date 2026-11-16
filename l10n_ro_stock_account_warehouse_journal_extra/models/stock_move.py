# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_account_move_ro_extra(self):
        account_moves = self.env["account.move"]
        for journal, moves in self._l10n_ro_split_by_stock_journal().items():
            if journal:
                moves = moves.with_context(l10n_ro_stock_journal_id=journal.id)
            account_moves |= super(StockMove, moves)._create_account_move_ro_extra()
        return account_moves

    def _fifo_neg_apply_compensation(self):
        journal = self._l10n_ro_get_warehouse_stock_journal()
        if journal:
            self = self.with_context(l10n_ro_stock_journal_id=journal.id)
        return super()._fifo_neg_apply_compensation()
