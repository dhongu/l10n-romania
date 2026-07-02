# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReportCommonTemplates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.company.partner_id
        cls.bank = cls.env["res.bank"].create({"name": "Banca Test"})
        cls.eur = cls.env.ref("base.EUR")
        cls.eur.active = True
        # cont în moneda companiei, bifat pentru tipărire
        cls.bank_acc = cls.env["res.partner.bank"].create(
            {
                "acc_number": "RO49AAAA1B31007593840000",
                "partner_id": cls.partner.id,
                "bank_id": cls.bank.id,
                "l10n_ro_print_report": True,
            }
        )
        # cont nebifat — nu trebuie să apară
        cls.bank_acc_hidden = cls.env["res.partner.bank"].create(
            {
                "acc_number": "RO12BBBB1B31007593840999",
                "partner_id": cls.partner.id,
                "bank_id": cls.bank.id,
                "l10n_ro_print_report": False,
            }
        )
        # cont bifat, dar în altă monedă decât documentul — nu trebuie să apară
        cls.bank_acc_eur = cls.env["res.partner.bank"].create(
            {
                "acc_number": "RO77CCCC1B31007593840777",
                "partner_id": cls.partner.id,
                "bank_id": cls.bank.id,
                "l10n_ro_print_report": True,
                "currency_id": cls.eur.id,
            }
        )

    def _render(self, template, values):
        return str(self.env["ir.qweb"]._render(template, values))

    def test_01_banks_template(self):
        html = self._render(
            "l10n_ro_report_common.banks",
            {"partner_id": self.partner, "res_company": self.company, "o": None},
        )
        self.assertIn(self.bank_acc.acc_number, html, "Contul bifat trebuie tipărit.")
        self.assertNotIn(self.bank_acc_hidden.acc_number, html, "Contul nebifat nu trebuie tipărit.")
        self.assertNotIn(
            self.bank_acc_eur.acc_number,
            html,
            "Contul în altă monedă decât a documentului nu trebuie tipărit.",
        )
        self.assertIn("Banca Test", html)

    def test_02_banks_template_document_currency(self):
        # `o` cu currency_id EUR (folosim chiar contul EUR ca document-surogat)
        # -> apare doar contul EUR, nu cel în moneda companiei
        html = self._render(
            "l10n_ro_report_common.banks",
            {
                "partner_id": self.partner,
                "res_company": self.company,
                "o": self.bank_acc_eur,
            },
        )
        self.assertIn(self.bank_acc_eur.acc_number, html)
        self.assertNotIn(self.bank_acc.acc_number, html)

    def test_03_banks_template_max_three(self):
        for i in range(4):
            self.env["res.partner.bank"].create(
                {
                    "acc_number": f"RO00DDDD1B3100759384{i:04d}",
                    "partner_id": self.partner.id,
                    "bank_id": self.bank.id,
                    "l10n_ro_print_report": True,
                }
            )
        html = self._render(
            "l10n_ro_report_common.banks",
            {"partner_id": self.partner, "res_company": self.company, "o": None},
        )
        shown = html.count("Account:")
        self.assertLessEqual(shown, 3, "Se tipăresc cel mult 3 conturi.")

    def test_04_report_address_company(self):
        self.partner.vat = "RO1234567897"
        self.partner.nrc = "J40/1234/2020"
        self.company.l10n_ro_share_capital = 45000.0
        html = self._render(
            "l10n_ro_report_common.report_address_company",
            {"res_company": self.company, "o": None},
        )
        self.assertIn(self.company.partner_id.name, html)
        self.assertIn("RO1234567897", html)
        self.assertIn("J40/1234/2020", html)
        self.assertIn("45000", html)
        self.assertIn(self.bank_acc.acc_number, html, "Blocul companiei include băncile.")

    def test_05_report_address_company_no_optional_fields(self):
        # setăm explicit 0 — la coexistența cu OCA l10n_ro_config, câmpul are default=200
        company = self.env["res.company"].create({"name": "Firma Fără Date", "l10n_ro_share_capital": 0.0})
        html = self._render(
            "l10n_ro_report_common.report_address_company",
            {"res_company": company, "o": None},
        )
        self.assertIn("Firma Fără Date", html)
        self.assertNotIn("Share Capital", html)
        self.assertNotIn("NRC", html)
