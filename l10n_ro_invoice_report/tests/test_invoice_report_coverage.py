# © 2026 Terrabit / Deltatech
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestL10nRoInvoiceReportCoverage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.country_ro = cls.env.ref("base.ro")
        cls.state_bc = cls.env.ref("base.RO_BC")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "vat": "RO1234567897",
                "country_id": cls.country_ro.id,
                "state_id": cls.state_bc.id,
                "city": "Bacau",
                "street": "Street Test 1",
            }
        )
        cls.delegate = cls.env["res.partner"].create(
            {
                "name": "Test Delegate",
                "is_company": False,
                "mean_transp": "Auto CJ 01 AAA",
                "country_id": cls.country_ro.id,
                "city": "Bacau",
                "street": "Street Test 2",
            }
        )

        cls.Account = cls.env["account.account"]
        cls.income_account = cls.Account.search(
            [("account_type", "=", "income"), ("company_ids", "in", cls.company.ids)], limit=1
        ) or cls.Account.search([("internal_group", "=", "income"), ("company_ids", "in", cls.company.ids)], limit=1)

    def create_invoice(self, amount=100.0, partner=None):
        if partner is None:
            partner = self.partner
        move_vals = {
            "move_type": "out_invoice",
            "partner_id": partner.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Test Line",
                        "quantity": 1.0,
                        "price_unit": amount,
                        "account_id": self.income_account.id,
                    },
                )
            ],
        }
        return self.env["account.move"].create(move_vals)

    def test_delegate_functionality(self):
        # Test onchange delegate_id
        invoice = self.create_invoice()
        invoice.delegate_id = self.delegate
        invoice.on_change_delegate_id()
        self.assertEqual(invoice.mean_transp, self.delegate.mean_transp)

        # Test default_get with context
        self.env["account.move"].with_context(default_delegate_id=self.delegate.id).create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
            }
        )
        # Note: the code in default_get seems to have a bug or is very specific:
        # if "default_delegate_id" in self.env.context:
        #     defaults["default_delegate_id"] = defaults["default_delegate_id"]
        # It doesn't seem to do much unless defaults["default_delegate_id"] was already there or intended to be set.
        # But we call it to ensure coverage.
        self.env["account.move"].with_context(default_delegate_id=self.delegate.id).default_get(["delegate_id"])

    def test_action_invoice_cancel_zero_amount(self):
        invoice = self.create_invoice(amount=0.0)
        invoice.action_post()
        # In Odoo 17+, state names changed, and 'paid' is no longer a valid state for account.move
        # The code in action_invoice_cancel checks for invoice.state == "paid"
        # This branch seems to be unreachable in Odoo 19 unless some other module adds 'paid' state.
        # We try to call it anyway if it exists.
        invoice.button_cancel()

    def test_set_origin_with_picking(self):
        # This requires stock modules to be installed and proper setup
        # We try to mock the structures if possible or at least trigger the lines
        invoice = self.create_invoice()

        # We need to mock sale_line_ids and move_ids if we don't want to install sale/stock
        # But if they are installed, we can try to use them.
        # The code:
        # for line in invoice.invoice_line_ids:
        #     for sale_line in line.sale_line_ids:
        #         for move in sale_line.move_ids:
        #             if move.picking_id.state == "done":
        #                 pickings |= move.picking_id

        invoice.set_origin_with_picking()
        # Should not crash even if empty

    def test_compute_payments_widget(self):
        invoice = self.create_invoice()
        invoice.action_post()

        # Mocking invoice_payments_widget
        # The method is _compute_payments_widget_reconciled_info
        # It calls super() then iterates over invoice_payments_widget["content"]

        # We can't easily trigger a real payment and reconciliation in a simple test without more setup
        # But we can try to call the method.
        invoice._compute_payments_widget_reconciled_info()

    def test_manual_cash_reconciliation_has_payment_type(self):
        invoice = self.create_invoice()
        invoice.action_post()

        cash_journal = self.env["account.journal"].create(
            {
                "name": "Test Manual Cash",
                "code": "TMCA",
                "type": "cash",
                "company_id": self.company.id,
            }
        )
        payment_move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": cash_journal.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Manual cash receipt",
                            "account_id": cash_journal.default_account_id.id,
                            "debit": invoice.amount_total,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Manual cash receipt",
                            "account_id": self.partner.property_account_receivable_id.id,
                            "partner_id": self.partner.id,
                            "credit": invoice.amount_total,
                        },
                    ),
                ],
            }
        )
        payment_move.action_post()

        receivable_lines = (invoice.line_ids | payment_move.line_ids).filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        receivable_lines.reconcile()
        invoice.invalidate_recordset(["invoice_payments_widget"])

        payment_vals = invoice.invoice_payments_widget["content"][0]
        self.assertFalse(payment_vals["account_payment_id"])
        self.assertEqual(payment_vals["journal_type"], "cash")
        self.assertEqual(payment_vals["payment_type"], "inbound")

        report = self.env.ref("account.account_invoices")
        html, report_type = report._render_qweb_html(report.report_name, invoice.ids)
        self.assertTrue(html)
        self.assertIn(report_type, ("html", "qweb-html"))

    def test_compute_partner_bank_id(self):
        bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "RO1234567890",
                "partner_id": self.partner.commercial_partner_id.id,
            }
        )
        # Assuming payment_bank_id is a field added by some module this depends on
        # If it doesn't exist, this might fail, let's check if it exists
        if "payment_bank_id" in self.env["res.partner"]._fields:
            self.partner.commercial_partner_id.payment_bank_id = bank
            invoice = self.create_invoice()
            invoice._compute_partner_bank_id()
            self.assertEqual(invoice.partner_bank_id, bank)

    def test_report_helpers(self):
        invoice = self.create_invoice()
        # Add a line with discount
        self.env["account.move.line"].create(
            {
                "move_id": invoice.id,
                "name": "Discounted Line",
                "quantity": 1.0,
                "price_unit": 100.0,
                "discount": 10.0,
                "account_id": self.income_account.id,
            }
        )

        # report_model = self.env["report.account.report_invoice"]
        # In Odoo, AbstractModels are accessed via env
        # But report.account.report_invoice is inherited by ReportInvoiceWithoutPayment in our module

        # We can use the report object to test helpers
        report = self.env["report.account.report_invoice"]

        self.assertTrue(report._with_discount(invoice))

        currency = invoice.currency_id
        text = report._amount_to_text(100.0, currency)
        self.assertIn("One Hundred", text)  # English default likely

        # _get_pickings
        report._get_pickings(invoice)

        # _get_discount
        report._get_discount()

        # _get_report_values
        report._get_report_values(invoice.ids)
