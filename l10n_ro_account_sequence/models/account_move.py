from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_ro_cash_document_type = fields.Selection(
        related="payment_id.l10n_ro_cash_document_type", readonly=True, store=True
    )

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super()._get_last_sequence_domain(relaxed=relaxed)
        if (
            self.journal_id
            and self.journal_id.type == "cash"
            and self.company_id.account_fiscal_country_id.code == "RO"
        ):
            payment = self.payment_id
            if payment:
                l10n_ro_cash_document_type = payment.l10n_ro_cash_document_type
                where_string += " AND l10n_ro_cash_document_type = %(l10n_ro_cash_document_type)s "
                param["l10n_ro_cash_document_type"] = l10n_ro_cash_document_type
        return where_string, param

    def _get_starting_sequence(self):
        starting_sequence = super()._get_starting_sequence()
        if (
            self.journal_id
            and self.journal_id.type == "cash"
            and self.company_id.account_fiscal_country_id.code == "RO"
        ):
            if self.journal_id.payment_sequence:
                starting_sequence = starting_sequence[1:]
            if self.payment_id.l10n_ro_cash_document_type == "internal_transfer":
                starting_sequence = "IT" + starting_sequence
            if self.payment_id.l10n_ro_cash_document_type == "customer_receipt":
                starting_sequence = "CH" + starting_sequence
            elif self.payment_id.l10n_ro_cash_document_type == "supplier_receipt":
                starting_sequence = "PL" + starting_sequence
            elif self.payment_id.l10n_ro_cash_document_type == "payment_disposal":
                starting_sequence = "DP" + starting_sequence
            elif self.payment_id.l10n_ro_cash_document_type == "cash_collection":
                starting_sequence = "DI" + starting_sequence

        return starting_sequence

    def _sequence_matches_date(self):
        res = super()._sequence_matches_date()
        if self.move_type in ["out_invoice", "out_refund"]:
            move_has_name = self.name and self.name != "/"
            if move_has_name:
                last_sequence = self._get_last_sequence()
                if last_sequence:
                    last_move = self.search([("name", "=", last_sequence)], limit=1)
                    if last_move.date > self.date:
                        res = False
        return res
