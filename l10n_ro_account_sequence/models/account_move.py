from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_ro_cash_document_type = fields.Selection(
        related="origin_payment_id.l10n_ro_cash_document_type", readonly=True, store=True
    )

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super()._get_last_sequence_domain(relaxed=relaxed)
        if self.journal_id and self.journal_id.type == "cash" and self.company_id.chart_template == "ro":
            # During posting, origin_payment_id might not yet be set. Use context fallback.
            payment = self.origin_payment_id
            l10n_ro_cash_document_type = None
            if payment:
                l10n_ro_cash_document_type = payment.l10n_ro_cash_document_type or "other"
            if not l10n_ro_cash_document_type:
                l10n_ro_cash_document_type = self.env.context.get("l10n_ro_cash_document_type", "other")
            where_string += " AND l10n_ro_cash_document_type = %(l10n_ro_cash_document_type)s "
            param["l10n_ro_cash_document_type"] = l10n_ro_cash_document_type
        return where_string, param

    def _get_starting_sequence(self):
        starting_sequence = super()._get_starting_sequence()
        if self.journal_id and self.journal_id.type == "cash" and self.company_id.chart_template == "ro":
            # Be robust to posting timing: origin_payment_id may not be set yet.
            payment = self.origin_payment_id or getattr(self, "payment_id", False)
            doc_type = None
            if payment:
                doc_type = payment.l10n_ro_cash_document_type
            if not doc_type:
                doc_type = self.env.context.get("l10n_ro_cash_document_type")
            # Replace core payment prefix 'P' for payments with specific RO prefix
            if starting_sequence and starting_sequence.startswith("P"):
                starting_sequence = starting_sequence[1:]
            if doc_type == "internal_transfer":
                starting_sequence = "IT" + starting_sequence
            elif doc_type == "customer_receipt":
                starting_sequence = "CH" + starting_sequence
            elif doc_type == "supplier_receipt":
                starting_sequence = "PL" + starting_sequence
            elif doc_type == "payment_disposal":
                starting_sequence = "DP" + starting_sequence
            elif doc_type == "cash_collection":
                starting_sequence = "DI" + starting_sequence

        return starting_sequence

    # def _sequence_matches_date(self):
    #     res = super()._sequence_matches_date()
    #     if self.move_type in ["out_invoice", "out_refund"] and self.state != "draft":
    #         move_has_name = self.name and self.name != "/"
    #         if move_has_name:
    #             last_sequence = self._get_last_sequence()
    #             if last_sequence:
    #                 last_move = self.search([("name", "=", last_sequence)], limit=1)
    #                 if last_move.date > self.date:
    #                     res = False
    #     return res
