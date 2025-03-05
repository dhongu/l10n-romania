from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    l10n_ro_journal_type = fields.Selection(related="journal_id.type", readonly=True, store=True)
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

    @api.onchange("posted_before", "state", "journal_id", "date")
    def _onchange_journal_date(self):
        # res = super()._onchange_journal_date()
        if not self.move_id.id:
            self.name = False
        # return res

    @api.onchange("payment_type", "partner_type", "is_internal_transfer", "journal_id")
    def _onchange_payment_type_and_partner_type(self):
        self.l10n_ro_cash_document_type = "other"
        if not self.journal_id:
            return
        if self.journal_id.type != "cash":
            return
        is_internal_transfer = (
            self.partner_id and self.partner_id == self.journal_id.company_id.partner_id and self.destination_journal_id
        )
        if is_internal_transfer:
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("l10n_ro_cash_document_type", False):
                if vals.get("journal_id"):
                    journal = self.env["account.journal"].browse(vals["journal_id"])
                    if journal.type != "cash":
                        vals["l10n_ro_cash_document_type"] = "other"
                        continue

                payment_type = vals.get("payment_type", "inbound")
                partner_type = vals.get("partner_type", "customer")
                if payment_type == "inbound":
                    vals["l10n_ro_cash_document_type"] = (
                        "customer_receipt" if partner_type == "customer" else "cash_collection"
                    )

                elif payment_type == "outbound":
                    vals["l10n_ro_cash_document_type"] = (
                        "supplier_receipt" if partner_type == "supplier" else "payment_disposal"
                    )

        return super().create(vals_list)
