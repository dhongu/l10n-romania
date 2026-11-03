# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi de ecran pentru fișa „Locații și operații de consum și dare în folosință".
#
# Seedează: compania RO cu locațiile Consum și Dare în folosință, un depozit nou (cu tipurile de
# operație Consum și Dare în folosință), un bon de consum validat și un produs cu greutate netă.
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_stock_base,stock_account,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_stock_base:TestStockBaseScreenshots --stop-after-init
# Baza nu trebuie să aibă instalat `l10n_ro_hide_net_weight`, care ascunde greutatea netă.
import unittest

from odoo.tests import tagged

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestStockBaseScreenshots(ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_base"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        env = cls.env
        company = cls.prepare_ro_company(name="Depozit Demo SRL")
        if "account_fiscal_country_id" not in company._fields:
            raise unittest.SkipTest("capturile cer modulul account (țara fiscală a companiei)")
        company.account_fiscal_country_id = env.ref("base.ro")
        admin = env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        for xmlid in (
            "stock.group_stock_user",
            "stock.group_stock_manager",
            "stock.group_stock_multi_locations",
            "uom.group_uom",  # fără el, tab-ul Inventar al produsului nu apare
        ):
            grp = env.ref(xmlid, raise_if_not_found=False)
            if grp:
                admin.group_ids = [(4, grp.id)]

        company._l10n_ro_create_stock_locations()
        cls.consume_location = company.l10n_ro_consume_location_id
        cls.usage_location = company.l10n_ro_usage_location_id
        # numele se ia din limba de la instalare; în capturile RO le vrem în română
        cls.consume_location.name = "Consum"
        cls.usage_location.name = "Dare în folosință"

        # depozitul îl creează un utilizator român: tipurile de operație primesc nume în română
        cls.warehouse = (
            env["stock.warehouse"]
            .with_context(lang="ro_RO")
            .create({"name": "Depozit Central", "code": "DC", "company_id": company.id})
        )
        cls.consume_type = cls.warehouse.l10n_ro_consume_type_id
        cls.usage_type = cls.warehouse.l10n_ro_usage_type_id

        # acțiune cu lista locațiilor RO (meniul standard pornește cu filtrul „Intern")
        cls.location_action = env["ir.actions.act_window"].create(
            {
                "name": "Locations",
                "res_model": "stock.location",
                "view_mode": "list,form",
                "domain": [("usage", "in", ["consume", "usage_giving"]), ("company_id", "=", company.id)],
            }
        )
        cls.location_action.with_context(lang="ro_RO").name = "Locații"

        cls.product = env["product.template"].create(
            {
                "name": "Detergent industrial 5 L",
                "type": "consu",
                "is_storable": True,
                "default_code": "DET-5L",
                "weight": 5.4,
                "volume": 0.01,
                "standard_price": 42.0,
            }
        )
        cls.product_variant = cls.product.product_variant_id
        # la creare, valoarea s-ar pierde: varianta nu există încă (vezi raportul fișei)
        cls.product.l10n_ro_net_weight = 5.0
        cls.stock_menu = env.ref("stock.menu_stock_root")
        env["stock.quant"]._update_available_quantity(cls.product_variant, cls.warehouse.lot_stock_id, 40)

        cls.picking = env["stock.picking"].create(
            {
                "picking_type_id": cls.consume_type.id,
                "location_id": cls.consume_type.default_location_src_id.id,
                "location_dest_id": cls.consume_type.default_location_dest_id.id,
                "origin": "Curățenie hală producție",
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_variant.id,
                            "product_uom_qty": 6,
                            "uom_id": cls.product_variant.uom_id.id,
                            "location_id": cls.consume_type.default_location_src_id.id,
                            "location_dest_id": cls.consume_type.default_location_dest_id.id,
                        },
                    )
                ],
            }
        )
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.picking.move_ids.quantity = 6
        cls.picking.button_validate()

    def _shots(self):
        return [
            {
                "url": f"action={self.location_action.id}&menu_id={self.stock_menu.id}&view_type=list",
                "name": "01_locatii_consum_dare.png",
                "wait": ".o_list_view",
                "eval": "true",  # pauza lasă rândurile listei să se randeze înainte de evidențiere
                "highlight": "td[name='usage']",
            },
            {
                "url": f"id={self.consume_location.id}&model=stock.location&view_type=form&menu_id={self.stock_menu.id}",
                "name": "02_locatie_consum.png",
                "wait": ".o_form_view",
                "highlight": "div[name='usage']",
            },
            {
                "path": f"/odoo/action-stock.action_warehouse_form/{self.warehouse.id}?debug=1",
                "name": "03_depozit_tipuri_operatie.png",
                "wait": ".o_form_view",
                "click_tab": {"ro_RO": "Informații tehnice", "en_US": "Technical Information"},
                "eval": "true",  # pauza din eval lasă tab-ul să se randeze înainte de evidențiere
                "highlight": ["div[name='l10n_ro_consume_type_id']", "div[name='l10n_ro_usage_type_id']"],
                "settle": 2000,
            },
            {
                "url": f"id={self.consume_type.id}&model=stock.picking.type&view_type=form",
                "name": "04_tip_operatie_consum.png",
                "wait": ".o_form_view",
                "highlight": ["div[name='sequence_code']", "div[name='default_location_dest_id']"],
                "settle": 2000,
            },
            {
                "url": f"id={self.picking.id}&model=stock.picking&view_type=form",
                "name": "05_bon_consum.png",
                "wait": ".o_form_view",
                "highlight": ["div[name='location_dest_id']", ".o_field_widget[name='name']"],
                "settle": 2000,
            },
            {
                "url": f"id={self.product.id}&model=product.template&view_type=form",
                "name": "06_produs_greutate_neta.png",
                "wait": ".o_form_view",
                "click_tab": {"ro_RO": "Inventar", "en_US": "Inventory"},
                "eval": "true",
                "highlight": ".o_field_widget[name='l10n_ro_net_weight']",
                "settle": 2000,
            },
        ]

    def test_capture_fise(self):
        self.capture_screenshots(self._shots())

    def test_capture_usage(self):
        self.capture_screenshots(self._shots(), lang="en_US")
