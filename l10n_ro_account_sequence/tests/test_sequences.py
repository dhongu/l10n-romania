# Copyright (C) 2025 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestL10nRoAccountSequence(TransactionCase):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.chart_template = "ro"

    def setUp(self):
        super().setUp()

        # Partners
        self.partner_customer = self.env["res.partner"].create({"name": "Customer A", "company_type": "company"})
        self.partner_supplier = self.env["res.partner"].create({"name": "Supplier B", "company_type": "company"})

        # Journals
        self.cash_journal = self.env["account.journal"].create(
            {
                "name": "Cash RO",
                "type": "cash",
            }
        )

        self.cash_journal.remove_outstanding_accounts()

        self.bank_journal = self.env["account.journal"].create(
            {
                "name": "Bank RO",
                "type": "bank",
            }
        )

    def _post_payment(self, vals):
        payment = self.env["account.payment"].create(vals)
        payment.action_post()
        self.assertTrue(payment.move_id, "Posted payment should have a move_id")
        self.assertTrue(payment.move_id.name and payment.move_id.name != "/", "Move should have a sequence name")
        return payment

    def test_prefix_customer_receipt_CH(self):
        payment = self._post_payment(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_customer.id,
                "amount": 100.0,
                "journal_id": self.cash_journal.id,
            }
        )
        self.assertEqual(payment.l10n_ro_cash_document_type, "customer_receipt")
        self.assertTrue(payment.move_id.name.startswith("CH"), f"Expected CH prefix, got {payment.move_id.name}")
        self.assertEqual(payment.move_id.l10n_ro_cash_document_type, "customer_receipt")

    def test_prefix_supplier_receipt_PL(self):
        payment = self._post_payment(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner_supplier.id,
                "amount": 50.0,
                "journal_id": self.cash_journal.id,
            }
        )
        self.assertEqual(payment.l10n_ro_cash_document_type, "supplier_receipt")
        self.assertTrue(payment.move_id.name.startswith("PL"), f"Expected PL prefix, got {payment.move_id.name}")
        self.assertEqual(payment.move_id.l10n_ro_cash_document_type, "supplier_receipt")

    def test_prefix_payment_disposal_DP(self):
        payment = self._post_payment(
            {
                "payment_type": "outbound",
                "partner_type": "customer",
                "partner_id": self.partner_customer.id,
                "amount": 75.0,
                "journal_id": self.cash_journal.id,
            }
        )
        self.assertEqual(payment.l10n_ro_cash_document_type, "payment_disposal")
        self.assertTrue(payment.move_id.name.startswith("DP"), f"Expected DP prefix, got {payment.move_id.name}")
        self.assertEqual(payment.move_id.l10n_ro_cash_document_type, "payment_disposal")

    def test_prefix_cash_collection_DI(self):
        # Inbound with partner_type supplier falls under cash_collection per module logic
        payment = self._post_payment(
            {
                "payment_type": "inbound",
                "partner_type": "supplier",
                "partner_id": self.partner_supplier.id,
                "amount": 25.0,
                "journal_id": self.cash_journal.id,
            }
        )
        self.assertEqual(payment.l10n_ro_cash_document_type, "cash_collection")
        self.assertTrue(payment.move_id.name.startswith("DI"), f"Expected DI prefix, got {payment.move_id.name}")
        self.assertEqual(payment.move_id.l10n_ro_cash_document_type, "cash_collection")

    def test_prefix_internal_transfer_IT(self):
        # For internal transfer, explicitly set the document type on create to avoid UI onchange reliance
        # dest_cash = self.env["account.journal"].create(
        #     {
        #         "name": "Cash Dest RO",
        #         "type": "cash",
        #     }
        # )
        payment = self._post_payment(
            {
                "payment_type": "outbound",
                "partner_type": "customer",
                "partner_id": self.env.company.partner_id.id,
                "amount": 10.0,
                "journal_id": self.cash_journal.id,
                # "destination_journal_id": dest_cash.id,
                "l10n_ro_cash_document_type": "internal_transfer",
            }
        )
        self.assertEqual(payment.l10n_ro_cash_document_type, "internal_transfer")
        self.assertTrue(payment.move_id.name.startswith("IT"), f"Expected IT prefix, got {payment.move_id.name}")
        self.assertEqual(payment.move_id.l10n_ro_cash_document_type, "internal_transfer")

    def test_no_prefix_for_non_cash_journal(self):
        payment = self._post_payment(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_customer.id,
                "amount": 100.0,
                "journal_id": self.bank_journal.id,
            }
        )
        # For non-cash journals, no RO cash prefixes should be applied
        prefixes = ("CH", "PL", "DP", "DI", "IT")
        self.assertFalse(
            payment.move_id.name.startswith(prefixes),
            f"Bank payment should not have cash prefix: {payment.move_id.name}",
        )

    def _tail_sequence_number(self, name):
        import re

        m = re.search(r"(\d+)$", name or "")
        self.assertTrue(m, f"Name should end with digits, got: {name}")
        return int(m.group(1))

    def test_month_change_resets_sequence_customer_receipt(self):
        # Jan payment
        p_jan = self._post_payment(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_customer.id,
                "amount": 10.0,
                "journal_id": self.cash_journal.id,
                "date": "2025-01-15",
            }
        )
        # Feb payment
        p_feb = self._post_payment(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_customer.id,
                "amount": 12.0,
                "journal_id": self.cash_journal.id,
                "date": "2025-02-01",
            }
        )
        # Prefixes correct
        self.assertTrue(p_jan.move_id.name.startswith("CH"))
        self.assertTrue(p_feb.move_id.name.startswith("CH"))
        # Annual numbering for cash: no monthly reset; February should increment within same year
        jan_no = self._tail_sequence_number(p_jan.move_id.name)
        feb_no = self._tail_sequence_number(p_feb.move_id.name)
        self.assertEqual(
            feb_no,
            jan_no + 1,
            f"Expected February sequence to increment by 1, got {feb_no} vs {jan_no} from {p_feb.move_id.name}",
        )
        self.assertGreaterEqual(jan_no, 1)

    def test_year_change_resets_sequence_supplier_receipt(self):
        # Dec 2024 payment
        p_dec = self._post_payment(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner_supplier.id,
                "amount": 20.0,
                "journal_id": self.cash_journal.id,
                "date": "2024-12-31",
            }
        )
        # Jan 2025 payment
        p_jan = self._post_payment(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.partner_supplier.id,
                "amount": 22.0,
                "journal_id": self.cash_journal.id,
                "date": "2025-01-01",
            }
        )
        # Prefixes correct
        self.assertTrue(p_dec.move_id.name.startswith("PL"))
        self.assertTrue(p_jan.move_id.name.startswith("PL"))
        # Year boundary should reset sequence; January should start at 1
        dec_no = self._tail_sequence_number(p_dec.move_id.name)
        jan_no = self._tail_sequence_number(p_jan.move_id.name)
        self.assertEqual(jan_no, 1, f"Expected new year sequence to reset to 1, got {jan_no} from {p_jan.move_id.name}")
        self.assertGreaterEqual(dec_no, 1)
