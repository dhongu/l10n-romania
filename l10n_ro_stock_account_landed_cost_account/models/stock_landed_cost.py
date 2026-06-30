# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    def _create_account_move_line(self, credit_account_id, debit_account_id, remaining_qty):
        # Odoo 19: the core signature dropped ``move``, ``qty_out`` and
        # ``already_out_account_id`` (the "already out" handling was moved out of
        # this method) and renamed ``qty_out`` -> ``remaining_qty``.
        stock_move = self.move_id

        location_from = stock_move.location_id
        location_to = stock_move.location_dest_id
        from_account = location_from.l10n_ro_property_stock_valuation_account_id
        to_account = location_to.l10n_ro_property_stock_valuation_account_id

        if stock_move._is_in():
            debit_account_id = to_account.id or debit_account_id

        if stock_move._is_out():
            debit_account_id = from_account.id or debit_account_id

        fiscal_position = self.cost_id.account_journal_id.l10n_ro_fiscal_position_id
        if fiscal_position:
            credit_account_id = fiscal_position.map_account(self.env["account.account"].browse(credit_account_id)).id
            debit_account_id = fiscal_position.map_account(self.env["account.account"].browse(debit_account_id)).id

        lines = super()._create_account_move_line(credit_account_id, debit_account_id, remaining_qty)
        return self._l10n_ro_route_class6_through_intermediary(lines)

    def _l10n_ro_route_class6_through_intermediary(self, lines):
        """Route class 6 (expense) credit lines through the technical intermediary
        account, so a landed cost move keeps two clean balanced notes
        (stock valuation = intermediary account and intermediary account = class 6)
        instead of crediting a class 6 account directly. Class 609 is never
        rerouted. Active only when the company landed cost method is set to
        'intermediary' and an intermediary account is configured; otherwise the
        standard behaviour is preserved."""
        company = self.cost_id.company_id
        if company.l10n_ro_landed_cost_method != "intermediary":
            return lines
        intermediary_account = company.l10n_ro_landed_cost_intermediary_account_id
        if not intermediary_account:
            return lines

        new_lines = []
        for command in lines:
            vals = command[2]
            account = self.env["account.account"].browse(vals.get("account_id"))
            credit = vals.get("credit") or 0.0
            is_class_6 = account.code and account.code.startswith("6") and not account.code.startswith("609")
            if is_class_6 and credit:
                # 1) original credit line -> intermediary account (pairs with the stock valuation debit)
                new_lines.append([0, 0, dict(vals, account_id=intermediary_account.id)])
                # 2) intermediary account on debit (pairs with the class 6 credit below)
                new_lines.append([0, 0, dict(vals, account_id=intermediary_account.id, credit=0.0, debit=credit)])
                # 3) class 6 account credited against the intermediary account
                new_lines.append([0, 0, dict(vals, account_id=account.id)])
            else:
                new_lines.append(command)
        return new_lines
