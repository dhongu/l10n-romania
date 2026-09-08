# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from lxml import etree

from odoo.tests import tagged

from odoo.addons.l10n_ro_edi.tests.common import TestROEdiCommon

NS = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


@tagged("post_install_l10n", "post_install", "-at_install")
class TestMonetaryTotalPayable(TestROEdiCommon):
    """Cât timp factura nu e stinsă, XML-ul trimis la ANAF trebuie să declare
    ``cbc:PrepaidAmount`` = 0 și ``cbc:PayableAmount`` = totalul facturii.

    Comportamentul e cerut de livrările cu plata la ramburs: încasarea se
    înregistrează în Odoo pe fluxul de curierat, dar factura trebuie să ceară
    tot totalul, nu doar restul de plată din Odoo.

    Regresia pe care o prinde testul: pe 19.0 logica stătea pe
    ``_add_invoice_monetary_total_vals``, un hook care în standard e ``pass`` și
    nu mai e apelat de nimeni -- ``super()`` mergea, deci nu apărea nicio eroare,
    dar valorile nu ajungeau niciodată în XML. De aceea testul verifică XML-ul
    generat, nu metoda în izolare.
    """

    def _payable_and_prepaid(self, invoice):
        xml, errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(invoice)
        self.assertFalse([error for error in (errors or []) if "PayableAmount" in str(error)])
        tree = etree.fromstring(xml)
        total = tree.find("cac:LegalMonetaryTotal", NS)
        self.assertIsNotNone(total, "Factura nu are cac:LegalMonetaryTotal")
        return (
            float(total.find("cbc:PayableAmount", NS).text),
            float(total.find("cbc:PrepaidAmount", NS).text),
        )

    def test_unpaid_invoice_declares_full_total(self):
        invoice = self.create_invoice()
        self.assertNotEqual(invoice.payment_state, "paid")
        payable, prepaid = self._payable_and_prepaid(invoice)
        self.assertEqual(prepaid, 0.0)
        self.assertEqual(payable, invoice.amount_total)

    def test_partially_paid_invoice_still_declares_full_total(self):
        """Cazul de ramburs: o plată alocată în Odoo nu trebuie să reducă suma cerută."""
        invoice = self.create_invoice()
        self._register_payment(invoice, invoice.amount_total / 2)
        self.assertEqual(invoice.payment_state, "partial")
        self.assertAlmostEqual(invoice.amount_residual, invoice.amount_total / 2, places=2)

        payable, prepaid = self._payable_and_prepaid(invoice)
        self.assertEqual(prepaid, 0.0)
        self.assertEqual(payable, invoice.amount_total)

    def test_paid_invoice_keeps_standard_behaviour(self):
        """Factura stinsă rămâne pe comportamentul standard (BT-115 = BT-112 - BT-113)."""
        invoice = self.create_invoice()
        self._register_payment(invoice, invoice.amount_total)
        self.assertEqual(invoice.payment_state, "paid")

        payable, prepaid = self._payable_and_prepaid(invoice)
        self.assertEqual(payable, 0.0)
        self.assertEqual(prepaid, invoice.amount_total)

    def _register_payment(self, invoice, amount):
        payment = (
            self.env["account.payment.register"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "amount": amount,
                    "payment_date": invoice.invoice_date,
                    "journal_id": self.company_data["default_journal_bank"].id,
                }
            )
            ._create_payments()
        )
        self.assertTrue(payment)
        return payment
