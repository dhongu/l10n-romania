# Copyright (C) 2025 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestL10nRoAccountSequence(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        # Inheriting from AccountTestInvoicingCommon (instead of TransactionCase)
        # actually loads the RO chart of accounts: the decorator only sets
        # ``country_code`` while the chart is installed by the base setUpClass.
        # Without it partners have no receivable/payable account and the payment
        # counterpart line is created with account_id NULL.
        super().setUpClass()

        # Partners
        # Odoo 20: ``company_type`` is gone (``is_company`` is computed); it is
        # irrelevant for the numbering anyway.
        cls.partner_customer = cls.env["res.partner"].create({"name": "Customer A"})
        cls.partner_supplier = cls.env["res.partner"].create({"name": "Supplier B"})

        # Journals
        cls.cash_journal = cls.env["account.journal"].create(
            {
                "name": "Cash RO",
                "type": "cash",
            }
        )

        # Reuse the common bank journal: its payment method lines already have an
        # outstanding account configured, which Odoo 19 requires to generate the
        # journal entry on posting. A freshly created bank journal would have none,
        # so the payment would stay in 'in_process' without a move.
        cls.bank_journal = cls.company_data["default_journal_bank"]

        # Cash journal with a fixed code, used to assert the exact numbers
        # (the values were captured on Odoo 19 with the 19.0 module).
        cls.cash_journal_fixed = cls.env["account.journal"].create({"name": "Casa RO", "type": "cash", "code": "CASA"})

    def _post_payment(self, vals):
        payment = self.env["account.payment"].create(vals)
        payment.action_post()
        self.assertTrue(payment.move_id, "Posted payment should have a move_id")
        self.assertTrue(payment.move_id.name and payment.move_id.name != "/", "Move should have a sequence name")
        return payment

    def test_cash_journal_uses_default_account_for_both_payment_directions(self):
        lines = self.cash_journal.inbound_payment_method_line_ids + self.cash_journal.outbound_payment_method_line_ids
        self.assertTrue(lines, "Cash journal should provide payment method lines")
        self.assertTrue(all(line.payment_account_id == self.cash_journal.default_account_id for line in lines))

    def test_cash_journal_realigns_payment_accounts_when_default_account_changes(self):
        new_account = self.env["account.account"].search(
            [
                ("company_ids", "in", self.env.company.id),
                ("account_type", "=", "asset_cash"),
                ("id", "!=", self.cash_journal.default_account_id.id),
            ],
            limit=1,
        )
        if not new_account:
            new_account = self.env["account.account"].create(
                {
                    "name": "Cash RO Secondary",
                    "code": "531199",
                    "account_type": "asset_cash",
                    "company_ids": [(4, self.env.company.id)],
                }
            )

        self.cash_journal.write({"default_account_id": new_account.id})
        lines = self.cash_journal.inbound_payment_method_line_ids + self.cash_journal.outbound_payment_method_line_ids
        self.assertTrue(all(line.payment_account_id == new_account for line in lines))

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
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_customer.id,
                "amount": 100.0,
                "journal_id": self.bank_journal.id,
            }
        )
        payment.action_post()
        # In Odoo 19 a bank payment is only set to 'in_process' on posting and the
        # journal entry is generated when it is validated (e.g. via bank
        # reconciliation). Force validation so the move exists to assert against.
        if not payment.move_id:
            payment.action_validate()
        self.assertTrue(payment.move_id, "Validated bank payment should have a move_id")
        self.assertTrue(payment.move_id.name and payment.move_id.name != "/", "Move should have a sequence name")
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

    # ------------------------------------------------------------------
    # Exact numbers: identical to the ones generated by the 19.0 module
    # ------------------------------------------------------------------

    def _pay(self, payment_type, partner_type, partner, date, journal=None, **extra):
        vals = {
            "payment_type": payment_type,
            "partner_type": partner_type,
            "partner_id": partner.id,
            "amount": 10.0,
            "journal_id": (journal or self.cash_journal_fixed).id,
            "date": date,
        }
        vals.update(extra)
        payment = self.env["account.payment"].create(vals)
        payment.action_post()
        if not payment.move_id:
            payment.action_validate()
        return payment

    def _cash_entry(self, date):
        journal = self.cash_journal_fixed
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": journal.id,
                "date": date,
                "line_ids": [
                    (0, 0, {"account_id": journal.default_account_id.id, "debit": 5.0, "credit": 0.0}),
                    (
                        0,
                        0,
                        {
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 0.0,
                            "credit": 5.0,
                        },
                    ),
                ],
            }
        )
        move.action_post()
        return move

    def test_exact_numbers_per_cash_document_type(self):
        company_partner = self.env.company.partner_id
        cases = [
            # (payment_type, partner_type, partner, date, extra, document type, expected number)
            ("inbound", "customer", self.partner_customer, "2025-03-10", {}, "customer_receipt", "CHCASA/2025/00001"),
            ("inbound", "customer", self.partner_customer, "2025-03-11", {}, "customer_receipt", "CHCASA/2025/00002"),
            ("outbound", "supplier", self.partner_supplier, "2025-03-10", {}, "supplier_receipt", "PLCASA/2025/00001"),
            ("outbound", "customer", self.partner_customer, "2025-03-10", {}, "payment_disposal", "DPCASA/2025/00001"),
            ("inbound", "supplier", self.partner_supplier, "2025-03-10", {}, "cash_collection", "DICASA/2025/00001"),
            (
                "outbound",
                "customer",
                company_partner,
                "2025-03-10",
                {"l10n_ro_cash_document_type": "internal_transfer"},
                "internal_transfer",
                "ITCASA/2025/00001",
            ),
            (
                "inbound",
                "customer",
                self.partner_customer,
                "2025-03-10",
                {"l10n_ro_cash_document_type": "other"},
                "other",
                "CASA/2025/00001",
            ),
            (
                "inbound",
                "customer",
                self.partner_customer,
                "2025-03-12",
                {"l10n_ro_cash_document_type": "other"},
                "other",
                "CASA/2025/00002",
            ),
            # another month: annual numbering, each document type keeps its own counter
            ("outbound", "supplier", self.partner_supplier, "2025-04-01", {}, "supplier_receipt", "PLCASA/2025/00002"),
            ("inbound", "customer", self.partner_customer, "2025-04-01", {}, "customer_receipt", "CHCASA/2025/00003"),
        ]
        for payment_type, partner_type, partner, date, extra, doc_type, expected in cases:
            payment = self._pay(payment_type, partner_type, partner, date, **extra)
            self.assertEqual(payment.l10n_ro_cash_document_type, doc_type)
            self.assertEqual(payment.move_id.l10n_ro_cash_document_type, doc_type)
            self.assertEqual(payment.move_id.name, expected)
            self.assertEqual(payment.name, expected)

        # manual cash entries (no payment) continue the journal sequence without prefix
        self.assertEqual(self._cash_entry("2025-03-10").name, "CASA/2025/00003")
        entry = self._cash_entry("2025-03-15")
        self.assertEqual(entry.name, "CASA/2025/00004")
        self.assertFalse(entry.l10n_ro_cash_document_type)

        # reset to draft + re-post keeps the number
        payment = self._pay("inbound", "customer", self.partner_customer, "2025-05-05")
        self.assertEqual(payment.move_id.name, "CHCASA/2025/00004")
        payment.action_draft()
        payment.action_post()
        self.assertEqual(payment.move_id.name, "CHCASA/2025/00004")

    def test_exact_numbers_year_change(self):
        self.assertEqual(
            self._pay("outbound", "supplier", self.partner_supplier, "2024-12-31").move_id.name,
            "PLCASA/2024/00001",
        )
        self.assertEqual(
            self._pay("outbound", "supplier", self.partner_supplier, "2025-01-01").move_id.name,
            "PLCASA/2025/00001",
        )
        self.assertEqual(
            self._pay("outbound", "supplier", self.partner_supplier, "2026-01-02").move_id.name,
            "PLCASA/2026/00001",
        )

    def test_exact_numbers_bank_journal_unchanged(self):
        bank = self.bank_journal
        first = self._pay("inbound", "customer", self.partner_customer, "2025-03-10", journal=bank)
        second = self._pay("inbound", "customer", self.partner_customer, "2025-03-10", journal=bank)
        self.assertEqual(first.move_id.name, f"P{bank.code}/2025/00001")
        self.assertEqual(second.move_id.name, f"P{bank.code}/2025/00002")

    def test_form_onchange_cash_document_type(self):
        # ``partner_type`` is invisible on the form: it comes from the action context
        payment_model = self.env["account.payment"].with_context(
            default_payment_type="outbound", default_partner_type="supplier"
        )
        with Form(payment_model) as form:
            form.journal_id = self.cash_journal_fixed
            form.partner_id = self.partner_supplier
            form.amount = 10.0
            form.date = "2025-03-10"
            self.assertEqual(form.l10n_ro_cash_document_type, "supplier_receipt")
            form.payment_type = "inbound"
            self.assertEqual(form.l10n_ro_cash_document_type, "cash_collection")
            form.l10n_ro_cash_document_type = "customer_receipt"
            self.assertEqual(form.partner_type, "customer")
        payment = form.save()
        payment.action_post()
        self.assertEqual(payment.move_id.name, "CHCASA/2025/00001")
