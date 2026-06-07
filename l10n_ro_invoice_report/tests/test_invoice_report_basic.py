# © 2025 Terrabit / Deltatech
# Basic sanity tests for l10n_ro_invoice_report
# Goal: ensure the report action exists, templates are available, and report renders.

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestL10nRoInvoiceReportBasics(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env
        cls.company = cls.env.company

    def test_report_action_and_templates_exist(self):
        # Report action should be registered
        action = self.env.ref("l10n_ro_invoice_report.account_invoices_in_company_language")
        self.assertEqual(action.model, "account.move")
        # Main template should exist
        template_view = self.env.ref("l10n_ro_invoice_report.report_invoice_company_language")
        self.assertEqual(template_view._name, "ir.ui.view")

    def test_render_report_on_minimal_invoice(self):
        Partner = self.env["res.partner"]
        Account = self.env["account.account"]
        Move = self.env["account.move"]

        partner = Partner.create({"name": "Test Customer"})
        # Try to get a reasonable income account
        income_account = (
            Account.search([("account_type", "=", "income")], limit=1)
            or Account.search([("internal_group", "=", "income")], limit=1)
            or Account.search([("deprecated", "=", False)], limit=1)
        )
        self.assertTrue(income_account, "No account found to use on invoice line.")

        move_vals = {
            "move_type": "out_invoice",
            "partner_id": partner.id,
            # let default sale journal be picked by Odoo for the company
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Test Line",
                        "quantity": 1.0,
                        "price_unit": 100.0,
                        "account_id": income_account.id,
                    },
                )
            ],
        }
        move = Move.create(move_vals)
        # Do not require posting; the report should render in draft as well

        action_xmlid = "l10n_ro_invoice_report.account_invoices_in_company_language"
        html, html_type = self.env["ir.actions.report"]._render_qweb_html(action_xmlid, move.ids)
        self.assertIsInstance(html, (bytes, bytearray))
        self.assertGreater(len(html), 0)
        self.assertIn(html_type, ("html", "qweb-html"))
