# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi de ecran pentru fișa „Ascunderea greutății nete de pe produs".
#
# Seedează un produs stocabil cu masă, greutate netă și volum completate; captura arată tab-ul
# Inventar al produsului, unde greutatea netă nu mai apare.
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_hide_net_weight,stock_account,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_hide_net_weight:TestHideNetWeightScreenshots --stop-after-init
import unittest

from odoo.tests import tagged

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestHideNetWeightScreenshots(ScreenshotCase or object):
    screenshots_module = "l10n_ro_hide_net_weight"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        env = cls.env
        company = cls.prepare_ro_company(name="Depozit Demo SRL")
        admin = env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        for xmlid in ("stock.group_stock_user", "stock.group_stock_manager", "uom.group_uom"):
            grp = env.ref(xmlid, raise_if_not_found=False)
            if grp:
                admin.group_ids = [(4, grp.id)]
        cls.product = env["product.template"].create(
            {
                "name": "Detergent industrial 5 L",
                "type": "consu",
                "is_storable": True,
                "default_code": "DET-5L",
                "weight": 5.4,
                "volume": 0.01,
            }
        )
        # valoarea rămâne în bază, doar câmpul nu se mai vede
        cls.product.l10n_ro_net_weight = 5.0
        cls.stock_menu = env.ref("stock.menu_stock_root")

    def _shots(self):
        return [
            {
                "url": f"id={self.product.id}&model=product.template&view_type=form&menu_id={self.stock_menu.id}",
                "name": "01_produs_fara_greutate_neta.png",
                "wait": ".o_form_view",
                "click_tab": {"ro_RO": "Inventar", "en_US": "Inventory"},
                "eval": "true",  # pauza din eval lasă tab-ul să se randeze înainte de evidențiere
                # Masă și Volum, între care stătea Greutatea netă
                "highlight": ["div.o_row[name='weight']", "div.o_row[name='volume']"],
                "settle": 2000,
            },
        ]

    def test_capture_fise(self):
        self.capture_screenshots(self._shots())

    def test_capture_usage(self):
        self.capture_screenshots(self._shots(), lang="en_US")
