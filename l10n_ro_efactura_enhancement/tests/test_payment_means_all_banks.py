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
    facturii, nu doar contul de pe factura.

    Pe Odoo 20 res.partner.bank nu mai are currency_id: moneda contului e cea a
    jurnalului bancar legat, iar un cont fara jurnal e in moneda companiei.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        cls.eur = cls.env.ref("base.EUR")
        cls.eur.active = True
        cls.icp = cls.env["ir.config_parameter"].sudo()

    def _create_banks(self):
        # conturile se creeaza dupa postarea facturii: un cont nou, neincrezut,
        # ar bloca postarea (RedirectWarning „not trusted")
        def bank(account_number, print_report):
            return self.env["res.partner.bank"].create(
                {
                    "account_number": account_number,
                    "partner_id": self.company.partner_id.id,
                    "l10n_ro_print_report": print_report,
                }
            )

        self.bank_ron_1 = bank("RO49AAAA1B31007593840000", True)
        self.bank_ron_2 = bank("RO66BACX0000001234567890", True)
        self.bank_ron_hidden = bank("RO09BCYP0000001234567890", False)
        self.bank_eur = bank("RO56TREZ0000001234567890", True)
        self.env["account.journal"].create(
            {
                "name": "Banca EUR",
                "code": "BEUR",
                "type": "bank",
                "currency_id": self.eur.id,
                "bank_account_id": self.bank_eur.id,
                "company_id": self.company.id,
            }
        )

    def _payee_accounts(self, move):
        xml, _errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(move)
        tree = etree.fromstring(xml)
        return {
            node.findtext("cbc:ID", namespaces=NS)
            for node in tree.findall("cac:PaymentMeans/cac:PayeeFinancialAccount", NS)
        }

    def test_all_printed_banks_in_invoice_currency(self):
        invoice = self.create_invoice()
        self._create_banks()
        invoice.partner_bank_id = self.bank_ron_1
        self.icp.set_str("efactura.get_all_banks", "True")

        self.assertEqual(
            self._payee_accounts(invoice),
            {self.bank_ron_1.sanitized_account_number, self.bank_ron_2.sanitized_account_number},
        )

    def test_only_invoice_bank_when_disabled(self):
        invoice = self.create_invoice()
        self._create_banks()
        invoice.partner_bank_id = self.bank_ron_1
        self.icp.set_str("efactura.get_all_banks", "False")

        self.assertEqual(self._payee_accounts(invoice), {self.bank_ron_1.sanitized_account_number})
