# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _l10n_ro_get_warehouse_stock_journal(self):
        """Stock journal of the warehouse the move leaves or enters.

        An empty recordset means the stock journal of the company. A move
        between two warehouses with different journals is refused, as in 18.0:
        its entry cannot belong to both journals.
        """
        self.ensure_one()
        journals = self.env["account.journal"]
        for location in (self.location_id, self.location_dest_id):
            if location.usage == "internal" and location.warehouse_id:
                journals |= location.warehouse_id.with_company(self.company_id).l10n_ro_property_stock_journal_id
        if len(journals) > 1:
            raise UserError(
                self.env._(
                    "Transfer between warehouses with different stock journals is not allowed: %(journals)s.",
                    journals=", ".join(journals.mapped("display_name")),
                )
            )
        return journals

    def _l10n_ro_split_by_stock_journal(self):
        moves_by_journal = defaultdict(lambda: self.browse())
        for move in self:
            journal = self.env["account.journal"]
            if move._should_create_account_move():
                journal = move._l10n_ro_get_warehouse_stock_journal()
            moves_by_journal[journal] |= move
        return moves_by_journal

    def _create_account_move(self):
        # The standard groups the moves per company and partner and posts every
        # entry in the stock journal of the company; the warehouse journal is
        # swapped in by account.move.create, one group of moves per journal.
        account_moves = self.env["account.move"]
        for journal, moves in self._l10n_ro_split_by_stock_journal().items():
            if journal:
                moves = moves.with_context(l10n_ro_stock_journal_id=journal.id)
            account_moves |= super(StockMove, moves)._create_account_move()
        return account_moves

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
