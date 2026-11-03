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
class TestPaymentMeansAllBanks(TestROEdiCommon):
    """Cu ``efactura.get_all_banks`` activ, XML-ul e-Factura contine toate conturile
    firmei bifate ``l10n_ro_print_report`` (camp din l10n_ro_report_common) in moneda
    facturii, nu doar contul de pe factura."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.company_data["company"]
        ron = company.currency_id
        eur = cls.env.ref("base.EUR")
        eur.active = True

        def bank(acc_number, currency, print_report):
            return cls.env["res.partner.bank"].create(
                {
                    "acc_number": acc_number,
                    "partner_id": company.partner_id.id,
                    "currency_id": currency.id,
                    "l10n_ro_print_report": print_report,
                    "allow_out_payment": True,
                }
            )

        cls.bank_ron_1 = bank("RO49AAAA1B31007593840000", ron, True)
        cls.bank_ron_2 = bank("RO66BACX0000001234567890", ron, True)
        cls.bank_ron_hidden = bank("RO09BCYP0000001234567890", ron, False)
        cls.bank_eur = bank("RO56TREZ0000001234567890", eur, True)

    def _payee_accounts(self, move):
        xml, _errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(move)
        tree = etree.fromstring(xml)
        return {
            node.findtext("cbc:ID", namespaces=NS)
            for node in tree.findall("cac:PaymentMeans/cac:PayeeFinancialAccount", NS)
        }

    def test_all_printed_banks_in_invoice_currency(self):
        self.env["ir.config_parameter"].sudo().set_param("efactura.get_all_banks", "True")
        invoice = self.create_invoice(partner_bank_id=self.bank_ron_1.id)

        self.assertEqual(
            self._payee_accounts(invoice),
            {self.bank_ron_1.sanitized_acc_number, self.bank_ron_2.sanitized_acc_number},
        )

    def test_only_invoice_bank_when_disabled(self):
        self.env["ir.config_parameter"].sudo().set_param("efactura.get_all_banks", "False")
        invoice = self.create_invoice(partner_bank_id=self.bank_ron_1.id)

        self.assertEqual(self._payee_accounts(invoice), {self.bank_ron_1.sanitized_acc_number})
