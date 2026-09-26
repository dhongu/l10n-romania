# © 2026 Terrabit / Deltatech
# Tests for the cash payment/receipt order printed from a payment.

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestL10nRoPaymentReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create({"name": "Popescu Maria"})
        cls.cash_journal = cls.env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", cls.company.id)], limit=1
        ) or cls.env["account.journal"].create(
            {"name": "Casa", "type": "cash", "code": "CSHPR", "company_id": cls.company.id}
        )
        cls.bank_journal = cls.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", cls.company.id)], limit=1
        )

    def _payment(self, journal, payment_type="outbound", amount=250.0):
        payment = self.env["account.payment"].create(
            {
                "payment_type": payment_type,
                "partner_type": "supplier" if payment_type == "outbound" else "customer",
                "partner_id": self.partner.id,
                "amount": amount,
                "journal_id": journal.id,
                "memo": "Restituire numerar",
            }
        )
        payment.action_post()
        return payment

    def _render(self, payment):
        report = self.env.ref("l10n_ro_invoice_report.action_report_payment")
        html, _report_type = report._render_qweb_html(report.report_name, payment.ids)
        return html.decode() if isinstance(html, bytes) else html

    def test_cash_payment_order_is_complete(self):
        """Dispoziția de plată în numerar poartă codul formularului și casieria, fără semnături."""
        payment = self._payment(self.cash_journal)
        html = self._render(payment)

        self.assertIn("Payment disposal", html)
        self.assertIn("Form 14-4-4", html)
        self.assertIn(self.cash_journal.name, html, "casieria trebuie să apară pe document")
        self.assertIn("Identity document", html)
        self.assertIn(self.partner.name, html)
        self._assert_no_signature_block(html)

    def test_cash_receipt_order_uses_its_own_form_code(self):
        payment = self._payment(self.cash_journal, payment_type="inbound")
        html = self._render(payment)

        self.assertIn("Form 14-4-1", html)
        self.assertIn("Payer", html, "cel care aduce banii la casierie e plătitorul")
        self.assertNotIn("Depositor", html)
        self.assertNotIn("Identity document", html, "actul de identitate se cere doar la plată")
        self._assert_no_signature_block(html)

    def _assert_no_signature_block(self, html):
        """Blocul de semnături a fost eliminat din formular (tichet #9535)."""
        for label in ("Manager", "Cashier", "Amount received", "Amount deposited"):
            self.assertNotIn(label, html)

    def test_bank_payment_has_no_cash_desk_form(self):
        """La bancă nu e vorba de un formular de casă: fără cod sau casierie."""
        if not self.bank_journal:
            self.skipTest("Nu există jurnal de bancă în companie")
        payment = self._payment(self.bank_journal)
        html = self._render(payment)

        self.assertNotIn("Form 14-4-4", html)
        self.assertNotIn("Cash desk", html)
        self.assertNotIn("Cashier", html)
