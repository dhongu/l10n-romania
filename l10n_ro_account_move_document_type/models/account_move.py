from odoo import api, fields, models

DOCUMENT_TYPES = [
    ("invoice", "Invoice"),
    ("credit_note", "Credit Note"),
    ("vendor_bill", "Vendor Bill"),
    ("vendor_credit_note", "Vendor Credit Note"),
    ("sales_receipt", "Sales Receipt"),
    ("purchase_receipt", "Purchase Receipt"),
    ("customs_declaration", "Import (DVI)"),
    ("bank_statement", "Bank Statement"),
    ("cash_document", "Cash Document"),
    ("customer_receipt", "Customer Receipt"),
    ("supplier_receipt", "Supplier Receipt"),
    ("payment_disposal", "Payment Disposal"),
    ("cash_collection", "Cash Collection Disposal"),
    ("payroll", "Payroll"),
    ("expense_report", "Expense Report"),
    ("journal_entry", "Journal Entry"),
]

MOVE_TYPE_DOCUMENT_TYPE = {
    "out_invoice": "invoice",
    "out_refund": "credit_note",
    "in_invoice": "vendor_bill",
    "in_refund": "vendor_credit_note",
    "out_receipt": "sales_receipt",
    "in_receipt": "purchase_receipt",
}

JOURNAL_TYPE_DOCUMENT_TYPE = {
    "bank": "bank_statement",
    "cash": "cash_document",
}


class AccountMove(models.Model):
    _inherit = "account.move"

    # Documentul justificativ al înregistrării (Legea contabilității 82/1991, art. 6): pe facturi
    # rezultă din tipul notei, pe notele contabile îl completează modulul care le creează (DVI,
    # registrul de casă) sau contabilul.
    l10n_ro_document_type = fields.Selection(
        DOCUMENT_TYPES,
        string="Document Type",
        compute="_compute_l10n_ro_document_type",
        store=True,
        readonly=False,
        copy=False,
        help="Supporting document of the entry, shown in the Romanian journals and registers. "
        "Invoices take it from their type; on journal entries it is set by the module that creates "
        "them (customs declaration, cash register) or chosen by the accountant.",
    )

    @api.depends("move_type", "journal_id.type", "origin_payment_id", "statement_line_id")
    def _compute_l10n_ro_document_type(self):
        for move in self:
            move.l10n_ro_document_type = move._l10n_ro_get_document_type()

    def _l10n_ro_get_document_type(self):
        """Tipul documentului dedus din notă; modulele care știu mai mult îl suprascriu."""
        self.ensure_one()
        if self.move_type in MOVE_TYPE_DOCUMENT_TYPE:
            return MOVE_TYPE_DOCUMENT_TYPE[self.move_type]
        if self.origin_payment_id or self.statement_line_id:
            return JOURNAL_TYPE_DOCUMENT_TYPE.get(self.journal_id.type, "journal_entry")
        return "journal_entry"
