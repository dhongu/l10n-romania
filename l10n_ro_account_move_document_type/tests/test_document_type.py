# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import tagged
from odoo.tools import SQL

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ro_account_move_document_type.hooks import fill_document_type


@tagged("post_install", "-at_install")
class TestL10nRoDocumentType(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        # adresă completă: `l10n_ro_efactura_enhancement`, dacă e instalat, nu postează factura fără ea
        cls.partner_a.write(
            {
                "country_id": cls.env.ref("base.ro").id,
                "state_id": cls.env.ref("base.RO_B").id,
                "city": "București",
                "street": "Str. Exemplu 1",
            }
        )

    def test_invoice_types(self):
        for move_type, doc_type in [
            ("out_invoice", "invoice"),
            ("out_refund", "credit_note"),
            ("in_invoice", "vendor_bill"),
            ("in_refund", "vendor_credit_note"),
            ("out_receipt", "sales_receipt"),
            ("in_receipt", "purchase_receipt"),
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
        # nota plății stă pe contul de plăți în curs: o justifică ordinul de plată, nu extrasul
        self.assertEqual(payment.move_id.l10n_ro_document_type, "bank_document")

    def test_bank_statement_line(self):
        line = self.env["account.bank.statement.line"].create(
            {
                "journal_id": self.company_data["default_journal_bank"].id,
                "payment_ref": "Încasare client",
                "partner_id": self.partner_a.id,
                "amount": 50.0,
            }
        )
        self.assertEqual(line.move_id.l10n_ro_document_type, "bank_statement")

    def test_manual_import_vat_entry_gets_tax_line(self):
        """Fișa, pasul 2: taxa pe linia de bază (473) generează singură linia de TVA cu grila."""
        tax = self.env["account.chart.template"].ref("tvad_21")
        account_473 = self.env["account.account"].search(
            [("code", "=like", "473%"), ("company_ids", "in", [self.env.company.id])], limit=1
        )
        account_446 = self.env["account.account"].search(
            [("code", "=like", "4462%"), ("company_ids", "in", [self.env.company.id])], limit=1
        )
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ref": "26ROBU100000012345",
                "l10n_ro_document_type": "customs_declaration",
                "line_ids": [
                    (0, 0, {"account_id": account_473.id, "debit": 10000.0, "tax_ids": [(6, 0, tax.ids)]}),
                    (0, 0, {"account_id": account_446.id, "credit": 2100.0}),
                    (0, 0, {"account_id": account_473.id, "credit": 10000.0}),
                ],
            }
        )
        tax_line = move.line_ids.filtered("tax_line_id")
        self.assertEqual(len(tax_line), 1)
        self.assertEqual(tax_line.debit, 2100.0)
        self.assertTrue(tax_line.account_id.code.startswith("4426"))
        self.assertTrue(tax_line.tax_tag_ids)
        move.action_post()
        self.assertEqual(move.l10n_ro_document_type, "customs_declaration")

    def test_install_fill_matches_model(self):
        """Completarea în SQL de la instalare dă același tip ca regulile modelului."""
        moves = self.env["account.move"]
        for move_type in ("out_invoice", "out_refund", "in_invoice", "in_refund", "out_receipt", "in_receipt"):
            moves |= self.init_invoice(move_type, products=self.product_a, post=True)
        # plata prin casă rămâne în afara testului: `l10n_ro_account_sequence`, dacă e instalat, îi pune
        # tipul documentului de casă (prin migrarea lui, nu prin acest hook)
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
        moves |= payment.move_id
        for journal in (self.company_data["default_journal_bank"], self.company_data["default_journal_cash"]):
            moves |= (
                self.env["account.bank.statement.line"]
                .create({"journal_id": journal.id, "payment_ref": "Extras", "amount": 20.0})
                .move_id
            )
        moves |= self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": self.company_data["default_journal_misc"].id,
                "line_ids": [
                    (0, 0, {"account_id": self.company_data["default_account_expense"].id, "debit": 10.0}),
                    (0, 0, {"account_id": self.company_data["default_account_payable"].id, "credit": 10.0}),
                ],
            }
        )
        expected = {move.id: move._l10n_ro_get_document_type() for move in moves}
        # fiecare ramură a regulilor are cel puțin o notă
        self.assertEqual(
            set(expected.values()),
            {
                "invoice",
                "credit_note",
                "vendor_bill",
                "vendor_credit_note",
                "sales_receipt",
                "purchase_receipt",
                "bank_document",
                "bank_statement",
                "cash_document",
                "journal_entry",
            },
        )

        where = SQL("move.id IN %s", tuple(moves.ids))
        self.env.cr.execute(SQL("UPDATE account_move move SET l10n_ro_document_type = NULL WHERE %s", where))
        fill_document_type(self.env.cr, where)
        moves.invalidate_recordset(["l10n_ro_document_type"])
        self.assertEqual({move.id: move.l10n_ro_document_type for move in moves}, expected)
