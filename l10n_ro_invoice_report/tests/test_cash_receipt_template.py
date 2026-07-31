# © 2026 Terrabit / Deltatech
import re

from odoo import fields
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

TEMPLATE = "l10n_ro_invoice_report.report_cash_receipt"


def sentence_of(html):
    """Textul din blocul `payment_text`, așa cum îl randează un browser.

    Etichetele se elimină fără a pune nimic în loc - `</span><span>` nu produce
    spațiu la randare - iar spațiile albe rămase se colapsează. Înlocuirea
    etichetelor cu spațiu ar fabrica exact spațiile pe care le verificăm.
    """
    body = html.split('name="payment_text"', 1)[1].split("</div>", 1)[0]
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", body)).strip()


@tagged("post_install", "-at_install")
class TestCashReceiptTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Client Test S.R.L.",
                "vat": "RO47274592",
                "nrc": "J04/100/2010",
                "city": "Bacau",
                "street": "Str. Test 1",
            }
        )

    def _render(self, **overrides):
        values = {
            "res_company": self.company,
            "partner": self.partner,
            "payment_type": "inbound",
            "receipt_ref": "CH/2026/0001",
            "receipt_date": fields.Date.to_date("2026-01-31"),
            "amount": 500.0,
            "currency": self.company.currency_id,
            "documents": self.env["account.move"],
            "representing": False,
        }
        values.update(overrides)
        return str(self.env["ir.qweb"]._render(TEMPLATE, values))

    def test_01_no_space_before_comma(self):
        # regresia pentru care există șablonul unic: „S.R.L. , RO47274592" -
        # orice newline între două noduri se randează ca un spațiu, așa că
        # identificatorii trebuie construiți într-o singură expresie
        self.assertIn(
            "Client Test S.R.L., RO47274592, J04/100/2010, from Bacau, Str. Test 1,",
            sentence_of(self._render()),
        )

    def test_02_partner_without_identifiers_or_address(self):
        bare = self.env["res.partner"].create({"name": "Fara Date"})
        sentence = sentence_of(self._render(partner=bare))
        self.assertIn("Fara Date, amount", sentence)
        self.assertNotIn(" ,", sentence, "nicio virgulă rătăcită când lipsesc datele")
        self.assertNotIn(", from", sentence, "fără prepoziția de adresă când partenerul nu are adresă")

    def test_03_inbound_wording(self):
        html = self._render()
        self.assertIn("I received from", html)
        self.assertIn("Voucher:", html)
        self.assertNotIn("Payment disposal:", html)

    def test_04_outbound_wording(self):
        html = self._render(payment_type="outbound")
        self.assertIn("I payed to", html)
        self.assertIn("Payment disposal:", html)
        self.assertNotIn("I received from", html)

    def test_05_empty_company_identifiers_print_no_label(self):
        company = self.env["res.company"].create({"name": "Firma Fara Date"})
        html = self._render(res_company=company)
        self.assertNotIn("VAT:", html)
        self.assertNotIn("NRC:", html)

    def test_06_representing_free_text_only_without_documents(self):
        self.assertIn("avans marfa", self._render(representing="avans marfa"))

    def test_07_amount_in_words_is_printed(self):
        # cutia tipărește suma și în litere, oricare ar fi moneda
        text = self._render()
        expected = self.company.currency_id.amount_to_text(500.0)
        self.assertIn(expected, text)


@tagged("post_install", "-at_install")
class TestCashReceiptIntegration(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        # compania are moneda RON, deci se exercită și formularea românească
        # a sumei în litere
        super().setUpClass()
        cls.cash_journal = cls.company_data["default_journal_cash"]

    def _pay_in_cash(self, invoice):
        return (
            self.env["account.payment.register"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"journal_id": self.cash_journal.id})
            ._create_payments()
        )

    def test_01_payment_report_uses_the_shared_box(self):
        invoice = self._create_invoice_one_line(price_unit=500.0, tax_ids=[], post=True)
        payment = self._pay_in_cash(invoice)

        report = self.env.ref("l10n_ro_invoice_report.action_report_payment")
        html = report._render_qweb_html(report.report_name, payment.ids)[0].decode()

        self.assertIn("page-break-inside: avoid", html, "cutia comună trebuie randată")
        self.assertIn(invoice.name, html, "factura stinsă trebuie listată")
        self.assertNotIn(" ,", sentence_of(html))

    def test_02_amount_in_words_reaches_the_paper(self):
        # aici se verifică doar că suma în litere ajunge pe chitanță; *cum* este
        # formulată ține de res.currency.amount_to_text, testat în
        # l10n_ro_report_common, deci nu se fixează textul aici
        invoice = self._create_invoice_one_line(price_unit=500.0, tax_ids=[], post=True)
        payment = self._pay_in_cash(invoice)

        report = self.env.ref("l10n_ro_invoice_report.action_report_payment")
        html = report._render_qweb_html(report.report_name, payment.ids)[0].decode()

        self.assertIn(payment.currency_id.amount_to_text(payment.amount), html)

    def test_04_invoice_number_is_not_duplicated_in_the_title(self):
        # Odoo compune `ref` ca „PNUM/... (INV/...)" (account_move.py:1536), deci
        # titlul chitanței nu are voie să mai adauge o dată facturile stinse
        invoice = self._create_invoice_one_line(price_unit=500.0, tax_ids=[], post=True)
        self._pay_in_cash(invoice)

        report = self.env.ref("account.account_invoices")
        html = report._render_qweb_html(report.report_name, invoice.ids)[0].decode()
        titlu = html.split("page-break-inside: avoid", 1)[1].split('name="payment_text"', 1)[0]

        self.assertEqual(titlu.count(invoice.name), 1, f"numele facturii apare de mai multe ori în titlu: {titlu}")

    def test_03_invoice_pdf_appends_the_same_box(self):
        invoice = self._create_invoice_one_line(price_unit=500.0, tax_ids=[], post=True)
        self._pay_in_cash(invoice)

        report = self.env.ref("account.account_invoices")
        html = report._render_qweb_html(report.report_name, invoice.ids)[0].decode()

        self.assertIn("Representing counter value of invoice", html)
        self.assertIn(invoice.currency_id.amount_to_text(invoice.amount_total), html)
