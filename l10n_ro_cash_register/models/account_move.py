# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_ro_cash_registers_to_refresh(self):
        """Registrele de casă ale căror solduri sunt influențate de mișcările din `self`.

        Soldul unei zile se reportează în ziua următoare, deci o mișcare pe contul de casă
        înregistrată în ziua N invalidează registrul zilei N și pe toate cele ulterioare
        din același jurnal, nu doar registrul zilei respective.
        """
        register_model = self.env["l10n.ro.cash.register"]
        # Filtrul pe tipul contului elimină din start facturile și notele care nu ating
        # casieria, fără nicio interogare suplimentară.
        lines = self.line_ids.filtered(lambda line: line.account_id.account_type == "asset_cash")
        if not lines:
            return register_model

        journals = self.env["account.journal"].search(
            [
                ("type", "=", "cash"),
                ("default_account_id", "in", lines.account_id.ids),
                ("company_id", "in", lines.company_id.ids),
            ]
        )
        registers = register_model
        for journal in journals:
            dates = lines.filtered(
                lambda line, journal=journal: line.account_id == journal.default_account_id
                and line.company_id == journal.company_id
            ).mapped("date")
            dates = [date for date in dates if date]
            if not dates:
                continue
            # `sudo` pentru că postarea unei note nu presupune drept de scriere pe registru;
            # domeniul rămâne limitat la jurnalul atins, deci nu traversează companii.
            registers |= register_model.sudo().search([("journal_id", "=", journal.id), ("date", ">=", min(dates))])
        return registers

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        posted._l10n_ro_cash_registers_to_refresh().action_refresh()
        return posted

    def button_draft(self):
        # Registrele se determină înainte, cât timp notele sunt încă postate.
        registers = self._l10n_ro_cash_registers_to_refresh()
        res = super().button_draft()
        registers.action_refresh()
        return res

    def unlink(self):
        registers = self._l10n_ro_cash_registers_to_refresh()
        res = super().unlink()
        registers.action_refresh()
        return res
