from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    l10n_ro_journal_type = fields.Selection(
        related="journal_id.type", readonly=True, store=True
    )
    l10n_ro_cash_document_type = fields.Selection(
        [
            ("customer_receipt", "Customer Receipt"),
            ("supplier_receipt", "Supplier Receipt"),
            ("payment_disposal", "Payment Disposal"),
            ("cash_collection", "Cash Collection"),
            ("internal_transfer", "Internal Transfer"),
            ("other", "Other"),
        ],
        string="Cash Document Type",
        default="other",
        required=True,
    )

    @api.onchange("payment_type", "partner_type", "is_internal_transfer", "journal_id")
    def _onchange_payment_type_and_partner_type(self):
        self.l10n_ro_cash_document_type = "other"
        if not self.journal_id:
            return
        if self.journal_id.type != "cash":
            return
        if self.is_internal_transfer:
            self.l10n_ro_cash_document_type = "internal_transfer"
        elif self.payment_type == "inbound":
            if self.partner_type == "customer":
                self.l10n_ro_cash_document_type = "customer_receipt"
            else:
                self.l10n_ro_cash_document_type = "cash_collection"
        elif self.payment_type == "outbound":
            if self.partner_type == "supplier":
                self.l10n_ro_cash_document_type = "supplier_receipt"
            else:
                self.l10n_ro_cash_document_type = "payment_disposal"

    @api.onchange("l10n_ro_cash_document_type")
    def _onchange_l10n_ro_cash_document_type(self):
        if self.l10n_ro_cash_document_type == "customer_receipt":
            self.payment_type = "inbound"
            self.partner_type = "customer"
        elif self.l10n_ro_cash_document_type == "supplier_receipt":
            self.payment_type = "outbound"
            self.partner_type = "supplier"
        elif self.l10n_ro_cash_document_type == "cash_collection":
            self.payment_type = "inbound"
        elif self.l10n_ro_cash_document_type == "payment_disposal":
            self.payment_type = "outbound"
