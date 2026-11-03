# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# Capturi de ecran pentru fișa „Taxe implicite pentru produsele de tip serviciu".
# Seedează două produse prin formular (ca onchange-ul să ruleze exact ca în interfață):
# unul trecut pe Serviciu și unul trecut pe Serviciu și înapoi pe Bunuri.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_service_tax,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import unittest

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestServiceTaxScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_service_tax"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Firma Demo SRL")
        company = cls.env.company
        # browserul se autentifică cu admin: îl punem pe compania RO din test
        admin = cls.env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        ref = cls.env["account.chart.template"].with_company(company).ref
        # implicitele din planul RO, ca pe ecran să apară taxele reale, nu cele de test
        company.write(
            {
                "account_sale_tax_id": ref("tvac_21").id,
                "account_purchase_tax_id": ref("tvad_21").id,
            }
        )
        product_model = cls.env["product.template"].with_company(company)
        with Form(product_model) as product_form:
            product_form.name = "Servicii de consultanță"
            product_form.type = "service"
            product_form.list_price = 500
        cls.service = product_form.record
        with Form(product_model) as product_form:
            product_form.name = "Cablu UTP Cat6"
            product_form.type = "service"
            product_form.type = "consu"
            product_form.list_price = 120
        cls.goods = product_form.record
        # pe companie, ca prețul să apară în lei, nu în moneda companiei principale
        (cls.service | cls.goods).company_id = company
        cls.settings_action = cls.env.ref("account.action_account_config").id
        cls.product_action = cls.env.ref("account.product_product_action_sellable").id

    def _product_shot(self, product, name):
        return {
            "url": f"action={self.product_action}&id={product.id}&model=product.template&view_type=form",
            "name": name,
            "wait": ".o_form_view",
            "highlight": ["div[name='type']", "div[name='taxes_id']", "div[name='supplier_taxes_id']"],
            "settle": 2000,
        }

    def _shots(self):
        return [
            {
                "url": f"action={self.settings_action}",
                "name": "01_setari_taxe_servicii.png",
                "wait": "#l10n_ro_service_taxes",
                "timeout": 40000,
                "eval": "document.querySelector('#default_taxes').scrollIntoView({block: 'center'});",
                "highlight": ["#l10n_ro_service_taxes"],
                "settle": 2500,
            },
            self._product_shot(self.service, "02_produs_tip_serviciu.png"),
            self._product_shot(self.goods, "03_produs_revenire_bunuri.png"),
        ]

    def test_capture_fise(self):
        self.capture_screenshots(self._shots(), hide_systray=True)

    def test_capture_usage(self):
        self.capture_screenshots(self._shots(), hide_systray=True, lang="en_US")
