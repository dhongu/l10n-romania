# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from ..hooks import post_init_hook


@tagged("post_install", "-at_install")
class TestServiceTax(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        ref = cls.env["account.chart.template"].with_company(cls.company).ref
        # implicitele companiei (AccountTestInvoicingCommon le poate înlocui pe cele din plan)
        cls.sale_tax = cls.company.account_sale_tax_id
        cls.purchase_tax = cls.company.account_purchase_tax_id
        cls.serv_sale_tax = ref("tvac_21_s")
        cls.serv_purchase_tax = ref("tvad_21_s")

    def test_chart_template_sets_service_taxes(self):
        self.assertRecordValues(
            self.company,
            [
                {
                    "l10n_ro_account_serv_sale_tax_id": self.serv_sale_tax.id,
                    "l10n_ro_account_serv_purchase_tax_id": self.serv_purchase_tax.id,
                }
            ],
        )

    def test_post_init_hook_fills_only_empty_fields(self):
        other_tax = self.purchase_tax
        self.company.write(
            {
                "l10n_ro_account_serv_sale_tax_id": False,
                "l10n_ro_account_serv_purchase_tax_id": other_tax.id,
            }
        )
        post_init_hook(self.env)
        self.assertEqual(self.company.l10n_ro_account_serv_sale_tax_id, self.serv_sale_tax)
        self.assertEqual(self.company.l10n_ro_account_serv_purchase_tax_id, other_tax)

    def test_product_type_service_gets_service_taxes(self):
        with Form(self.env["product.template"].with_company(self.company)) as product_form:
            product_form.name = "Consultanță"
            product_form.type = "service"
            self.assertEqual(product_form.taxes_id[:], self.serv_sale_tax)
            self.assertEqual(product_form.supplier_taxes_id[:], self.serv_purchase_tax)

    def test_product_back_to_goods_gets_default_taxes(self):
        with Form(self.env["product.template"].with_company(self.company)) as product_form:
            product_form.name = "Produs"
            product_form.type = "service"
            product_form.type = "consu"
            self.assertEqual(product_form.taxes_id[:], self.sale_tax)
            self.assertEqual(product_form.supplier_taxes_id[:], self.purchase_tax)

    def test_manual_taxes_kept_when_leaving_service(self):
        with Form(self.env["product.template"].with_company(self.company)) as product_form:
            product_form.name = "Produs"
            product_form.type = "service"
            product_form.taxes_id.clear()
            product_form.taxes_id.add(self.sale_tax)
            product_form.type = "consu"
            self.assertEqual(product_form.taxes_id[:], self.sale_tax)

    def test_settings_edit_company_fields(self):
        settings = self.env["res.config.settings"].with_company(self.company).create({})
        self.assertEqual(settings.l10n_ro_serv_sale_tax_id, self.serv_sale_tax)
        settings.l10n_ro_serv_sale_tax_id = self.sale_tax
        settings.execute()
        self.assertEqual(self.company.l10n_ro_account_serv_sale_tax_id, self.sale_tax)
