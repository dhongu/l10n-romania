# Copyright (C) 2022 Terrabit
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
        self.bank = self.create_partner_bank("RO48RNCB0090000506460001")
        self.journal = self.create_journal("TBNK2MT940", self.bank, ron_curr)

        self.data = (
            "Referinta 221031S029321541, data valutei 31-10-2022, Decontare -"
            "Platitor  Test Partner BCR  RO24BREL0002002472400100  "
            "CODFISC 0-Beneficiar  NEXTERP ROMANIA SRL  RO48RNCB0090000506460001  "
            "CODFISC RO9731314-"
            "Detalii  /ROC/SERIA BTLAM NR 21036843 . . /RFB/31/20221028/20221031"
        )
        self.codewords = ["Referinta", "Platitor", "Beneficiar", "Detalii", "CODFISC"]
        self.transactions = [
            {
                "account_number": "RO24BREL0002002472400100",
                "partner_name": "Test Partner BCR",
                "amount": 1000.0,
                "payment_ref": "  /ROC/SERIA BTLAM NR 21036843 . . /RFB/31/20221028/20221031",  # noqa
                "ref": "221031S029321541",
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
        """Unit Test function get_subfields()."""
        parser = self.env["l10n.ro.account.bank.statement.import.mt940.parser"]
        parser = parser.with_context(type="mt940_ro_cec")
        res = parser.get_subfields(self.data, self.codewords)
        espected_res = {
            "Referinta": [
                "221031S029321541,",
                "data",
                "valutei",
                "31",
                "10",
                "2022,",
                "Decontare",
            ],
            "Platitor": [
                "",
                "Test",
                "Partner",
                "BCR",
                "",
                "RO24BREL0002002472400100",
                "",
            ],
            "CODFISC": ["RO9731314"],
            "Beneficiar": [
                "",
                "NEXTERP",
                "ROMANIA",
                "SRL",
                "",
                "RO48RNCB0090000506460001",
                "",
            ],
            "Detalii": [
                "",
                "/ROC/SERIA",
                "BTLAM",
                "NR",
                "21036843",
                ".",
                ".",
                "/RFB/31/20221028/20221031",
            ],
        }
        self.assertTrue(res == espected_res)

    def test_handle_common_subfields(self):
        """Unit Test function handle_common_subfields()."""
        parser = self.env["l10n.ro.account.bank.statement.import.mt940.parser"]
        parser = parser.with_context(type="mt940_ro_cec")
        subfields = parser.get_subfields(self.data, self.codewords)
        transaction = self.transactions[0]
        parser.handle_common_subfields(transaction, subfields)

    def test_statement_import(self):
        """A whole CEC statement must land as one bank statement with all its
        lines, balances and dates."""
        self._load_statement(self._testfile(), mt940_type="mt940_ro_cec")
        bank_statements = self.get_statements(self.journal.id)
        self.assertEqual(len(bank_statements), 1)
        statement = bank_statements[0]
        self.assertEqual(len(statement.line_ids), 4)
        self.assertEqual(statement.balance_start, 1000.0)
        self.assertEqual(statement.balance_end_real, 0.0)
        self.assertEqual(statement.date, fields.Date.from_string("2022-10-31"))

        self.assertEqual(
            sorted(statement.line_ids.mapped("amount")),
            [-243836.22, -4.0, -2.0, 1000.0],
        )
        incoming = statement.line_ids.filtered(lambda line: line.amount == 1000.0)
        self.assertEqual(incoming.ref, "2022103180931993")
        self.assertIn("Test Partner BCR", incoming.payment_ref)

        # This sample uses the "Platitor  NAME  IBAN  CODFISC" wording, which
        # the tag 86 regexes (built for "Platitor NAME,Iban Platitor IBAN,")
        # do not match, so no counterpart is extracted from it. The extraction
        # itself is covered by test_handle_tag_86_* below.
        self.assertFalse(statement.line_ids.filtered("account_number"))

    def test_is_cec(self):
        """The wizard must recognise a CEC statement both from the journal's
        BIC and from the explicit context flag, and stay out of the way
        otherwise."""
        self.bank.bank_id.bic = "CECEROBU"
        wizard = self.env["account.statement.import"].with_context(journal_id=self.journal.id)
        self.assertTrue(wizard._is_cec())

        wizard = self.env["account.statement.import"].with_context(mt940_ro_cec=True)
        self.assertTrue(wizard._is_cec())

        self.assertFalse(self.env["account.statement.import"]._is_cec())

    def test_parse_file_flagged_as_cec(self):
        """`_parse_file` must route through the CEC parser when the wizard is
        flagged as CEC, without the caller setting the parser `type` itself.
        This is the path a real import takes; passing `type` directly is
        served by the base module and bypasses this one."""
        with open(self._testfile(), "rb") as datafile:
            data_file = datafile.read()
        wizard = self.env["account.statement.import"].with_context(mt940_ro_cec=True)
        currency, account_number, statements = wizard._parse_file(data_file)
        self.assertEqual(currency, "RON")
        self.assertEqual(account_number, "RO48RNCB0090000506460001")
        self.assertEqual(len(statements), 1)

        statement = statements[0]
        self.assertEqual(statement["balance_start"], 1000.0)
        self.assertEqual(statement["balance_end_real"], 0.0)
        transactions = statement["transactions"]
        self.assertEqual(len(transactions), 4)
        self.assertEqual(transactions[0]["amount"], 1000.0)
        self.assertEqual(transactions[0]["ref"], "2022103180931993")
        # tag 86 is kept verbatim as both the label and the note
        self.assertEqual(transactions[0]["payment_ref"], transactions[0]["narration"])

    def test_parse_file_falls_back_when_not_mt940(self):
        """A file the CEC parser cannot make sense of must be handed back to
        the generic import chain rather than swallowed."""
        wizard = self.env["account.statement.import"].with_context(mt940_ro_cec=True)
        with self.assertRaises(UserError):
            wizard._parse_file(b"this is not an MT940 file")

    def test_post_parse_file_matches_partner_by_vat(self):
        """`_post_parse_file` turns a VAT number left on a transaction into a
        real partner, and drops the key either way."""
        partner = self.env["res.partner"].create({"name": "CEC Test Partner", "vat": "RO20744552", "is_company": True})
        wizard = self.env["account.statement.import"]
        data = (
            "RON",
            "RO48RNCB0090000506460001",
            [
                {
                    "transactions": [
                        {"amount": 1.0, "vat": "RO20744552"},
                        {"amount": 2.0, "vat": "RO00000000"},
                        {"amount": 3.0},
                    ]
                }
            ],
        )
        _currency, _account, statements = wizard._post_parse_file(data)
        matched, unmatched, plain = statements[0]["transactions"]
        self.assertEqual(matched["partner_id"], partner.id)
        self.assertEqual(matched["partner_name"], "CEC Test Partner")
        self.assertNotIn("vat", matched)
        self.assertNotIn("partner_id", unmatched)
        self.assertNotIn("vat", unmatched)
        self.assertNotIn("partner_id", plain)

    def test_handle_tag_86_extracts_beneficiary_on_debit(self):
        """On a payment out, the counterparty is the beneficiary: name, IBAN
        and VAT are read from the structured tag 86."""
        result = {"statement": {"transactions": [{"amount": -1000.0, "ref": "2022103180931993"}]}}
        self._parser().handle_tag_86(self._tag_86_beneficiary(), result)
        transaction = result["statement"]["transactions"][-1]
        self.assertEqual(transaction["partner_name"], "GB RICAMBI SPA")
        self.assertEqual(transaction["account_number"], "IT07K0100512900000000001681")
        # The reference parsed from tag 61 must survive tag 86 parsing.
        self.assertEqual(transaction["ref"], "2022103180931993")

    def test_handle_tag_86_extracts_payer_on_credit(self):
        """On a collection, the counterparty is the payer instead."""
        result = {"statement": {"transactions": [{"amount": 1000.0}]}}
        self._parser().handle_tag_86(self._tag_86_payer(), result)
        transaction = result["statement"]["transactions"][-1]
        self.assertEqual(transaction["partner_name"], "TEST PLATITOR SRL")
        self.assertEqual(transaction["account_number"], "RO24BREL0002002472400100")

    def test_handle_tag_86_matches_partner_by_vat(self):
        """The VAT number in tag 86 wins over the name scraped from the text:
        the line arrives attached to the partner already in the database."""
        partner = self.env["res.partner"].create({"name": "GB Ricambi SpA", "vat": "RO20744552", "is_company": True})
        result = {"statement": {"transactions": [{"amount": -1000.0}]}}
        self._parser().handle_tag_86(self._tag_86_beneficiary(), result)
        transaction = result["statement"]["transactions"][-1]
        self.assertEqual(transaction["partner_id"], partner.id)
        self.assertEqual(transaction["partner_name"], "GB Ricambi SpA")

    def test_handle_tag_86_edge_cases(self):
        """Tag 86 may arrive before any transaction, and it must not touch a
        transaction that already carries a name."""
        parser = self._parser()
        result = {"statement": {"transactions": []}}
        parser.handle_tag_86(self._tag_86_payer(), result)
        self.assertEqual(result["statement"]["transactions"], [])

        result = {"statement": {"transactions": [{"amount": 1.0, "name": "already set"}]}}
        parser.handle_tag_86(self._tag_86_payer(), result)
        transaction = result["statement"]["transactions"][-1]
        self.assertNotIn("payment_ref", transaction)
        self.assertNotIn("partner_name", transaction)

    def test_get_counterpart(self):
        """The CEC override maps the subfield triplet to IBAN, name and VAT;
        the third slot is read but deliberately not used."""
        parser = self._parser()
        self.assertIsNone(parser.get_counterpart({}, []))

        transaction = {}
        parser.get_counterpart(transaction, ["RO24BREL0002002472400100"])
        self.assertEqual(transaction["account_number"], "RO24BREL0002002472400100")
        self.assertNotIn("partner_name", transaction)

        # an empty IBAN slot must not overwrite anything
        transaction = {}
        parser.get_counterpart(transaction, ["", "TEST SRL"])
        self.assertNotIn("account_number", transaction)
        self.assertEqual(transaction["partner_name"], "TEST SRL")

        transaction = {}
        parser.get_counterpart(transaction, ["RO24BREL0002002472400100", "TEST SRL", "RO9731314"])
        self.assertEqual(transaction["account_number"], "RO24BREL0002002472400100")
        self.assertEqual(transaction["partner_name"], "TEST SRL")

    def test_get_codewords(self):
        """CEC files label their subfields in Romanian words, not numbers."""
        self.assertEqual(self._parser().get_codewords(), self.codewords)

    def test_handle_tag_28_sets_statement_name(self):
        """Real CEC files use tag 28C, so this CEC-specific tag 28 handler
        only shows up on files that use the plain tag."""
        result = {"statement": {"name": None}}
        self._parser().handle_tag_28("22304/1.", result)
        self.assertEqual(result["statement"]["name"], "22304/1")

    def test_parser_does_not_hijack_other_banks(self):
        """The CEC overrides must delegate to the generic parser for any other
        MT940 flavour, otherwise installing this module would break the import
        of every other bank in the same database."""
        parser = self.env["l10n.ro.account.bank.statement.import.mt940.parser"]
        cec = self._parser()
        other = parser.with_context(type="mt940_general")

        self.assertEqual(cec.get_header_lines(), 1)
        self.assertEqual(other.get_header_lines(), 0)
        self.assertEqual(cec.get_header_regex(), ":20:")
        self.assertEqual(other.get_header_regex(), ":940:")
        self.assertEqual(cec.get_subfield_split_text(), "-")
        self.assertEqual(other.get_subfield_split_text(), "/")
        self.assertNotEqual(cec.get_codewords(), other.get_codewords())
        self.assertNotEqual(cec.get_tag_61_regex().pattern, other.get_tag_61_regex().pattern)

        transaction = {}
        other.get_counterpart(transaction, ["RO24BREL0002002472400100", "TEST SRL"])
        self.assertEqual(transaction["partner_name"], "TEST SRL")

        result = {"statement": {"name": "keep me"}}
        other.handle_tag_28("22304/1.", result)
        self.assertEqual(result["statement"]["name"], "keep me")

        # tag 86 stays generic: the Romanian wording is not parsed at all
        result = {"statement": {"transactions": [{"amount": -1.0}]}}
        other.handle_tag_86(self._tag_86_beneficiary(), result)
        self.assertNotIn("account_number", result["statement"]["transactions"][0])

    def _parser(self):
        return self.env["l10n.ro.account.bank.statement.import.mt940.parser"].with_context(type="mt940_ro_cec")

    def _testfile(self):
        return file_path(
            "l10n_ro_account_bank_statement_import_mt940_cec/test_files/test_file_bcr.STA",
        )

    def _tag_86_beneficiary(self):
        return (
            "INVOICE NO. 16864,"
            "Beneficiar GB RICAMBI SPA,"
            "Iban Beneficiar IT07K0100512900000000001681,"
            "Banca beneficiar BNLIITRRMOX,"
            "CUI/CNP Beneficiar RO20744552,"
        )

    def _tag_86_payer(self):
        return (
            "INVOICE NO. 16864,"
            "Platitor TEST PLATITOR SRL,"
            "Iban Platitor RO24BREL0002002472400100,"
            "Banca platitor BRELROBU,"
            "CUI/CNP Platitor RO9731314,"
        )
