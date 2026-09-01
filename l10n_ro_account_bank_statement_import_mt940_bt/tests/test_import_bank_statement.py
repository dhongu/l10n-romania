# Copyright (C) 2016 Forest and Biomass Romania
# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.exceptions import UserError
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
        self.bank = self.create_partner_bank("RO86BTRL02901202800597XX")
        self.journal = self.create_journal("TBNK3MT940", self.bank, ron_curr)

        self.data = """000+20Plata           +30302410000+31RO89RZBR0000060003480121
+32NEXTERP ROMANIA SRL+33/
+23PLATA FACT 4603309"""
        self.codewords = [
            "20",
            "23",
            "24",
            "25",
            "26",
            "27",
            "30",
            "31",
            "32",
            "33",
            "61",
            "62",
        ]
        self.transactions = [
            {
                "account_number": "RO89RZBR0000060003480121",
                "partner_name": "NEXTERP ROMANIA SRL",
                "amount": 1000.0,
                "payment_ref": "/PLATA FACT 4603309",
                "ref": "OPH478PLATA",
            },
        ]

    def _prepare_statement_lines(self, statements):
        transact = self.transactions[0]
        for st_vals in statements[2]:
            for line_vals in st_vals["transactions"]:
                line_vals["amount"] = transact["amount"]
                line_vals["payment_ref"] = transact["payment_ref"]
                line_vals["account_number"] = transact["account_number"]
                line_vals["partner_name"] = transact["partner_name"]
                line_vals["ref"] = transact["ref"]

    def test_get_subfields(self):
        """BT does not override `get_subfields`, so it splits on "/" like the
        generic parser and does not understand the "+NN" layout used by BRD."""
        parser = self._parser()
        self.assertEqual(parser.get_subfield_split_text(), "/")
        res = parser.get_subfields(self.data, self.codewords)
        self.assertNotIn("32", res)

    def test_handle_common_subfields(self):
        """Unit Test function handle_common_subfields()."""
        parser = self.env["l10n.ro.account.bank.statement.import.mt940.parser"]
        parser = parser.with_context(type="mt940_ro_bt")
        subfields = parser.get_subfields(self.data, self.codewords)
        transaction = self.transactions[0]
        parser.handle_common_subfields(transaction, subfields)

    def test_statement_import(self):
        """A whole BT statement must land as one bank statement with all its
        lines, balances and dates."""
        self._load_statement(self._testfile(), mt940_type="mt940_ro_bt")
        bank_statements = self.get_statements(self.journal.id)
        self.assertEqual(len(bank_statements), 1)
        statement = bank_statements[0]
        self.assertEqual(len(statement.line_ids), 15)
        self.assertEqual(statement.balance_start, 38634.33)
        self.assertEqual(statement.balance_end_real, 70800.97)

        cash_in = statement.line_ids.filtered(lambda line: line.amount == 10600.0)
        self.assertEqual(len(cash_in), 1)
        self.assertEqual(cash_in.date, fields.Date.from_string("2025-01-08"))
        self.assertIn("Depunere numerar ATM", cash_in.payment_ref)

        # The lines carrying a C.I.F. are the ones the BT-specific parsing
        # exists for: they are the only ones that get a counterpart account.
        with_counterpart = statement.line_ids.filtered("account_number")
        self.assertEqual(len(with_counterpart), 2)
        incoming = statement.line_ids.filtered(lambda line: line.account_number == "RO60BTRLRONCRT0447604301")
        self.assertEqual(incoming.amount, 4821.0)
        self.assertEqual(incoming.date, fields.Date.from_string("2025-01-09"))
        self.assertIn("C.I.F.:20744552", incoming.payment_ref)

        payment = statement.line_ids.filtered(lambda line: line.amount == -4115.0)
        self.assertEqual(len(payment), 1)
        self.assertFalse(payment.account_number)

    def test_is_bt(self):
        """The wizard must recognise a BT statement both from the journal's
        BIC and from the explicit context flag, and stay out of the way
        otherwise."""
        self.bank.bank_id.bic = "BTRLRO22"
        wizard = self.env["account.statement.import"].with_context(journal_id=self.journal.id)
        self.assertTrue(wizard._is_bt())

        wizard = self.env["account.statement.import"].with_context(mt940_ro_bt=True)
        self.assertTrue(wizard._is_bt())

        self.assertFalse(self.env["account.statement.import"]._is_bt())

    def test_parse_file_flagged_as_bt(self):
        """`_parse_file` must route through the BT parser when the wizard is
        flagged as BT, without the caller setting the parser `type` itself.
        This is the path a real import takes; passing `type` directly is
        served by the base module and bypasses this one."""
        with open(self._testfile(), "rb") as datafile:
            data_file = datafile.read()
        wizard = self.env["account.statement.import"].with_context(mt940_ro_bt=True)
        currency, account_number, statements = wizard._parse_file(data_file)
        self.assertEqual(currency, "RON")
        self.assertEqual(account_number, "RO86BTRL02901202800597XX")
        self.assertEqual(len(statements), 1)

        statement = statements[0]
        self.assertEqual(statement["balance_start"], 38634.33)
        self.assertEqual(statement["balance_end_real"], 70800.97)
        transactions = statement["transactions"]
        self.assertEqual(len(transactions), 15)

        # Tag 61 gives every line its own unique import id, so re-importing
        # the same file cannot duplicate the lines.
        self.assertEqual(len({tx["unique_import_id"] for tx in transactions}), 15)

        incoming = next(tx for tx in transactions if tx.get("account_number") == "RO60BTRLRONCRT0447604301")
        self.assertEqual(incoming["amount"], 4821.0)
        self.assertEqual(incoming["partner_name"], "DIN 08.01 .2025 1 MAROCO AMBIENT SRL")

    def test_parse_file_falls_back_when_not_mt940(self):
        """A file the BT parser cannot make sense of must be handed back to
        the generic import chain rather than swallowed."""
        wizard = self.env["account.statement.import"].with_context(mt940_ro_bt=True)
        with self.assertRaises(UserError):
            wizard._parse_file(b"this is not an MT940 file")

    def test_handle_tag_86_matches_partner_by_cif(self):
        """The reason this module exists: the C.I.F. printed in tag 86 is
        looked up against the partners, so the statement line arrives already
        attached to the right one instead of the name scraped from the text."""
        partner = self.env["res.partner"].create(
            {"name": "MAROCO AMBIENT SRL", "vat": "RO20744552", "is_company": True}
        )
        with open(self._testfile(), "rb") as datafile:
            data_file = datafile.read()
        wizard = self.env["account.statement.import"].with_context(mt940_ro_bt=True)
        _currency, _account, statements = wizard._parse_file(data_file)
        incoming = next(
            tx for tx in statements[0]["transactions"] if tx.get("account_number") == "RO60BTRLRONCRT0447604301"
        )
        self.assertEqual(incoming["partner_id"], partner.id)
        self.assertEqual(incoming["partner_name"], "MAROCO AMBIENT SRL")

    def test_handle_tag_28_sets_statement_name(self):
        """Real BT files use tag 28C, so this BT-specific tag 28 handler only
        shows up on files that use the plain tag."""
        result = {"statement": {"name": None}}
        self._parser().handle_tag_28("00004/00001.", result)
        self.assertEqual(result["statement"]["name"], "00004/00001")

    def test_tag_handlers_tolerate_missing_transaction(self):
        """A tag 61 the BT regex cannot read opens no transaction, and a
        tag 86 can arrive before any transaction was opened. Neither handler
        may blow up on the empty list."""
        parser = self._parser()
        result = {"statement": {"transactions": []}, "account_number": None}
        parser.handle_tag_61("not a tag 61 body", result)
        self.assertEqual(result["statement"]["transactions"], [])
        parser.handle_tag_86("Depunere numerar ATM", result)
        self.assertEqual(result["statement"]["transactions"], [])

    def test_handle_tag_86_keeps_existing_payment_ref(self):
        """Tag 86 only supplies a payment reference when the transaction has
        none yet; an already parsed one must survive."""
        result = {
            "statement": {"transactions": [{"amount": 1.0, "payment_ref": "keep me"}]},
        }
        self._parser().handle_tag_86("Depunere numerar ATM", result)
        self.assertEqual(result["statement"]["transactions"][-1]["payment_ref"], "keep me")

    def test_parser_does_not_hijack_other_banks(self):
        """The BT overrides must delegate to the generic parser for any other
        MT940 flavour, otherwise installing this module would break the import
        of every other bank in the same database."""
        parser = self.env["l10n.ro.account.bank.statement.import.mt940.parser"]
        bt = parser.with_context(type="mt940_ro_bt")
        other = parser.with_context(type="mt940_general")

        self.assertEqual(bt.get_header_lines(), 1)
        self.assertEqual(other.get_header_lines(), 0)
        self.assertEqual(bt.get_header_regex(), "^{1:")
        self.assertEqual(other.get_header_regex(), ":940:")
        self.assertNotEqual(bt.get_tag_61_regex().pattern, other.get_tag_61_regex().pattern)

        result = {"account_number": None}
        other.handle_tag_25("RO86.BTRL02901202800597XX", result)
        self.assertEqual(result["account_number"], "RO86BTRL02901202800597XX")

        result = {"statement": {"name": "keep me"}}
        other.handle_tag_28("00004/00001.", result)
        self.assertEqual(result["statement"]["name"], "keep me")

        # tag 61 stays generic: no BT unique import id is stamped on it
        result = {"statement": {"transactions": []}, "account_number": None}
        other.handle_tag_61("250108C10600,00NMSCNONREF", result)
        self.assertEqual(len(result["statement"]["transactions"]), 1)
        self.assertNotIn("unique_import_id", result["statement"]["transactions"][0])

        # tag 86 stays generic: no C.I.F. lookup, no raw text as payment_ref
        result = {"statement": {"transactions": [{"amount": 1.0}]}}
        other.handle_tag_86("Incasare OP C.I.F.:20744552 SOME NAME RO60BTRL", result)
        self.assertEqual(result["statement"]["transactions"][0]["payment_ref"], "/")

    def _parser(self):
        return self.env["l10n.ro.account.bank.statement.import.mt940.parser"].with_context(type="mt940_ro_bt")

    def _testfile(self):
        return file_path(
            "l10n_ro_account_bank_statement_import_mt940_bt/test_files/test_bt_940.txt",
        )
