from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def print_cash_operation(self):
        pass

    def _l10n_ro_annex_count(self):
        """Numărul de documente justificative anexate actului de casă.

        Coloana „Nr. anexe" din formularul 14-4-7A numără documentele justificative
        care însoțesc actul de casă; echivalentul lor în Odoo sunt atașamentele notei
        contabile.
        """
        self.ensure_one()
        return len(self.move_id.attachment_ids)
