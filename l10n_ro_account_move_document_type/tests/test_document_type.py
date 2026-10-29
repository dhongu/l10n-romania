# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestL10nRoDocumentType(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()

    def test_invoice_types(self):
        for move_type, doc_type in [
            ("out_invoice", "invoice"),
            ("out_refund", "credit_note"),
            ("in_invoice", "vendor_bill"),
            ("in_refund", "vendor_credit_note"),
        ]:
            move = self.init_invoice(move_type, products=self.product_a)
            self.assertEqual(move.l10n_ro_document_type, doc_type, move_type)

    def test_journal_entry_default_and_manual(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": self.company_data["default_journal_misc"].id,
                "line_ids": [
                    (0, 0, {"account_id": self.company_data["default_account_expense"].id, "debit": 100.0}),
                    (0, 0, {"account_id": self.company_data["default_account_payable"].id, "credit": 100.0}),
                ],
            }
        )
        self.assertEqual(move.l10n_ro_document_type, "journal_entry")
        # nota de TVA la import introdusă manual: contabilul alege DVI-ul ca document justificativ
        move.l10n_ro_document_type = "customs_declaration"
        move.action_post()
        self.assertEqual(move.l10n_ro_document_type, "customs_declaration")

    def test_bank_payment(self):
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_a.id,
                "amount": 50.0,
                "journal_id": self.company_data["default_journal_bank"].id,
            }
        )
        payment.action_post()
        self.assertEqual(payment.move_id.l10n_ro_document_type, "bank_statement")
