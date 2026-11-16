# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi de ecran pentru fișa „Câmpurile contabilității de stoc românești, fără logică".
#
# Modulul nu are ecrane proprii: capturile arată modulul instalat în Aplicații și lista
# câmpurilor pe care le declară (Setări → Tehnic → Câmpuri, în modul dezvoltator).
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_stock_account_base,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_stock_account_base:TestStockAccountBaseScreenshots --stop-after-init
import unittest

from odoo.tests import tagged

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestStockAccountBaseScreenshots(ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_account_base"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        env = cls.env
        cls.prepare_ro_company(name="Depozit Demo SRL")
        cls.module = env["ir.module.module"].search([("name", "=", "l10n_ro_stock_account_base")])
        field_ids = (
            env["ir.model.data"]
            .search([("module", "=", "l10n_ro_stock_account_base"), ("model", "=", "ir.model.fields")])
            .mapped("res_id")
        )
        # lista câmpurilor declarate de modul (meniul tehnic arată toate câmpurile bazei)
        cls.fields_action = env["ir.actions.act_window"].create(
            {
                "name": "Fields",
                "res_model": "ir.model.fields",
                "view_mode": "list,form",
                "view_id": env.ref("base.view_model_fields_tree").id,
                "domain": [("id", "in", field_ids), ("name", "not in", ["id", "display_name"])],
                "context": {"group_by": ["model_id"]},
            }
        )
        cls.fields_action.with_context(lang="ro_RO").name = "Câmpuri"

    def _shots(self):
        return [
            {
                "path": f"/odoo/action-base.open_module_tree/{self.module.id}",
                "name": "01_modul_instalat.png",
                "wait": ".o_form_view",
                "settle": 2000,
            },
            {
                "path": f"/odoo/action-{self.fields_action.id}?debug=1",
                "name": "02_campuri_modul.png",
                "wait": ".o_list_view",
                # grupurile pe model se deschid ca să se vadă câmpurile fiecărui model
                "eval": "document.querySelectorAll('.o_group_header').forEach((h) => h.click())",
                "eval_wait": 2000,
                "settle": 2000,
            },
        ]

    def _capture(self, lang="ro_RO"):
        shots = self._shots()
        self.capture_screenshots(shots[:1], viewport=(1920, 950), lang=lang)
        # lista grupată pe modele e lungă și derulează în interiorul paginii, nu pe pagină
        self.capture_screenshots(shots[1:], viewport=(1920, 1750), lang=lang)

    def test_capture_fise(self):
        self._capture()

    def test_capture_usage(self):
        self._capture(lang="en_US")
