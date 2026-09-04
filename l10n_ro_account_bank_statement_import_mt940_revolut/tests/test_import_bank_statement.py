# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests import tagged
from odoo.tools.misc import file_path

from odoo.addons.l10n_ro_account_bank_statement_import_mt940_base.tests.common import (
    TestMT940BankStatementImport,
)


@tagged("post_install", "-at_install")
class TestImport(TestMT940BankStatementImport):
    def setUp(self):
        super().setUp()
        ron_curr = self.env.ref("base.RON")
        ron_curr.write({"active": True})
        self.bank = self.create_partner_bank("RO21REVO0000000000000000")
        self.journal = self.create_journal("TBNK4MT940", self.bank, ron_curr)
        self.parser = self.env["l10n.ro.account.bank.statement.import.mt940.parser"].with_context(
            type="mt940_ro_revolut"
        )

    def test_get_tag_61_regex(self):
        """Revolut doesn't use the MARF/EREF/PREF/NONREF reference codewords
        the generic parser expects, and amounts can carry 0, 1 or 2 decimal
        digits, so both need a dedicated regex."""
        regex = self.parser.get_tag_61_regex()
        cases = [
            ("260627D78,31NMSCOMV 1891", "D", "78,31", "MSC", "OMV 1891"),
            ("260630D1638,NMSCW020 JYSK BACAU", "D", "1638,", "MSC", "W020 JYSK BACAU"),
            (
                "260626D1529,2NTRFFE/2026/6/000008",
                "D",
                "1529,2",
                "TRF",
                "FE/2026/6/000008",
            ),
            ("260626C5000,NTRFALIMENTARE CONT-", "C", "5000,", "TRF", "ALIMENTARE CONT-"),
        ]
        for data, sign, amount, type_, reference in cases:
            match = regex.match(data)
            self.assertTrue(match, f"Failed to match {data}")
            self.assertEqual(match.group("sign"), sign)
            self.assertEqual(match.group("amount"), amount)
            self.assertEqual(match.group("type"), type_)
            self.assertEqual(match.group("reference"), reference)

    def test_handle_tag_86(self):
        """The ^NN structured subfields must be split into payment_ref,
        partner_name and account_number."""
        result = {"statement": {"transactions": [{"amount": -1529.2}]}}
        data = (
            "^20CATRE TEST BUYER SPOLKA JAWNA . FE/2026/6/000008"
            "^22/OCMT/PLN 1230.00/RATE/0.81880301"
            "^32TEST BUYER SPOLKA JAWNA"
            "^38PL82000000000000000000000010"
        )
        self.parser.handle_tag_86(data, result)
        transaction = result["statement"]["transactions"][-1]
        self.assertEqual(
            transaction["payment_ref"],
            "CATRE TEST BUYER SPOLKA JAWNA . FE/2026/6/000008",
        )
        self.assertEqual(transaction["partner_name"], "TEST BUYER SPOLKA JAWNA")
        self.assertEqual(transaction["account_number"], "PL82000000000000000000000010")

    def test_handle_tag_86_continuation(self):
        """^21 continues the narrative started in ^20, and a card purchase
        (^23 only, no ^32/^38) must not set a counterpart."""
        result = {"statement": {"transactions": [{"amount": 5000.0}]}}
        data = (
            "^20BANI ADAUGATI PRIN TEST SUPPLIER SRL . ALIMENTARE CONT-PLATA IN"
            "^21TERBANCARA INSTANT"
            "^32TEST SUPPLIER SRL"
        )
        self.parser.handle_tag_86(data, result)
        transaction = result["statement"]["transactions"][-1]
        self.assertEqual(
            transaction["payment_ref"],
            "BANI ADAUGATI PRIN TEST SUPPLIER SRL . ALIMENTARE " "CONT-PLATA INTERBANCARA INSTANT",
        )
        self.assertEqual(transaction["partner_name"], "TEST SUPPLIER SRL")

        card_result = {"statement": {"transactions": [{"amount": -78.31}]}}
        self.parser.handle_tag_86("^20OMV 1891^23MASTERCARD 516760XXXXXX7955", card_result)
        card_transaction = card_result["statement"]["transactions"][-1]
        self.assertEqual(card_transaction["payment_ref"], "OMV 1891")
        self.assertNotIn("partner_name", card_transaction)
        self.assertNotIn("account_number", card_transaction)

    def test_statement_import(self):
        """Only the RON wallet has a matching journal, the EUR/GBP/USD
        wallets in the same file must be dropped rather than blocking the
        import."""
        testfile = file_path(
            "l10n_ro_account_bank_statement_import_mt940_revolut/test_files/" "test_revolut_940.txt",
        )
        self._load_statement(testfile, mt940_type="mt940_ro_revolut")
        bank_statements = self.get_statements(self.journal.id)
        self.assertTrue(bank_statements)
        lines = bank_statements.line_ids
        self.assertEqual(len(lines), 14)

        card_purchase = lines.filtered(lambda line: line.payment_ref == "W020 JYSK BACAU C2")
        self.assertEqual(len(card_purchase), 1)
        self.assertEqual(card_purchase.amount, -1638.0)
        self.assertEqual(card_purchase.date, fields.Date.from_string("2026-06-30"))

        transfer = lines.filtered(lambda line: line.partner_name == "TEST BUYER SPOLKA JAWNA")
        self.assertEqual(len(transfer), 1)
        self.assertEqual(transfer.account_number, "PL82000000000000000000000010")
        self.assertEqual(transfer.amount, -1529.2)

        topup = lines.filtered(lambda line: line.partner_name == "TEST SUPPLIER SRL" and line.amount == 5000.0)
        self.assertEqual(len(topup), 2)

    def test_statement_import_multiple_currency_journals(self):
        """When a second journal (in another currency) is linked to the same
        IBAN, its wallet must be imported too, instead of being dropped
        because the currency-less journal lookup only ever found the first
        journal on that IBAN (see _revolut_journal_exists)."""
        eur_curr = self.env.ref("base.EUR")
        eur_journal = self.create_journal("TBNK5MT940", self.bank, eur_curr)

        testfile = file_path(
            "l10n_ro_account_bank_statement_import_mt940_revolut/test_files/" "test_revolut_940.txt",
        )
        self._load_statement(testfile, mt940_type="mt940_ro_revolut")

        ron_lines = self.get_statements(self.journal.id).line_ids
        self.assertEqual(len(ron_lines), 14)

        eur_lines = self.get_statements(eur_journal.id).line_ids
        self.assertEqual(len(eur_lines), 3)
        self.assertAlmostEqual(sum(eur_lines.mapped("amount")), 1249.53)
