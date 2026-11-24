# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi de ecran pentru fișa „Controale contabile la stoc: sursa liniilor de factură și prețul
# unitar nenul al mișcărilor".
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> \
#       -i l10n_ro_stock_account_enhancement,sale_stock_margin,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_stock_account_enhancement:TestStockAccountEnhancementScreenshots \
#       --stop-after-init
import unittest

from odoo.tests import tagged

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None

MODAL = ".modal-dialog .modal-body"
SETTING = "#l10n_ro_check_storable_line_source"
# caută cheile modulului în bara de căutare, ca filtrul să apară ca fațetă
SEARCH_PARAMS = """
    () => {
        const input = document.querySelector('.o_searchview_input');
        input.value = 'l10n_ro_stock_account.';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        setTimeout(() => input.dispatchEvent(
            new KeyboardEvent('keydown', {key: 'Enter', bubbles: true})), 500);
    }
"""


@tagged("-at_install", "post_install", "fise_screenshots")
class TestStockAccountEnhancementScreenshots(ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_account_enhancement"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        env = cls.env
        if "purchase_price" not in env["sale.order.line"]._fields:
            raise unittest.SkipTest("Captura livrării cere sale_stock_margin instalat")
        cls.company = cls.prepare_ro_company(name="Depozit Demo SRL")
        env.ref("base.user_admin").group_ids |= env.ref("l10n_ro_config.group_ro_menus")
        icp = env["ir.config_parameter"].sudo()
        icp.set_param("l10n_ro_stock_account.check_storable_line_source", "True")
        icp.set_param("l10n_ro_stock_account.skip_price_unit_check", "False")

        cls.customer = env["res.partner"].create({"name": "Client Demo SRL", "is_company": True})
        cls.vendor = env["res.partner"].create({"name": "Furnizor Demo SRL", "is_company": True})
        cls.categ = env["product.category"].create(
            {"name": "Mărfuri FIFO", "property_cost_method": "fifo", "property_valuation": "real_time"}
        )
        cls.product = env["product.product"].create(
            {
                "name": "Marfă fără cost",
                "is_storable": True,
                "categ_id": cls.categ.id,
                "list_price": 100.0,
                "standard_price": 0.0,
            }
        )

        cls.out_invoice = cls._draft_invoice("out_invoice", cls.customer)
        cls.in_invoice = cls._draft_invoice("in_invoice", cls.vendor)

        order = env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "order_line": [(0, 0, {"product_id": cls.product.id, "product_uom_qty": 1.0})],
            }
        )
        order.action_confirm()
        cls.picking = order.picking_ids
        cls.picking.picking_type_id.warehouse_id.name = "Depozit central"
        cls.picking.move_ids.write({"quantity": 1.0, "picked": True})

    @classmethod
    def _draft_invoice(cls, move_type, partner):
        return cls.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": partner.id,
                "invoice_date": "2026-11-16",
                "invoice_line_ids": [(0, 0, {"product_id": cls.product.id, "quantity": 1.0, "price_unit": 100.0})],
            }
        )

    def _shots(self):
        return [
            {
                "url": f"action={self.env.ref('account.action_account_config').id}",
                "name": "01_setare_verificare_sursa.png",
                "wait": ".o_setting_box",
                "timeout": 60000,
                # Setările arată doar aplicația selectată în stânga
                "click_btn": ".settings_tab [data-key='l10n_ro_config']",
                "wait_after": SETTING,
                "eval": f"document.querySelector('{SETTING}').scrollIntoView({{block: 'end'}})",
                "highlight": SETTING,
                "settle": 2000,
            },
            {
                "path": f"/odoo/action-account.action_move_out_invoice_type/{self.out_invoice.id}",
                "name": "02_factura_client_fara_comanda.png",
                "click_btn": "button[name='action_post']",
                "wait_after": MODAL,
            },
            {
                "path": f"/odoo/action-account.action_move_in_invoice_type/{self.in_invoice.id}",
                "name": "03_factura_furnizor_fara_comanda.png",
                "click_btn": "button[name='action_post']",
                "wait_after": MODAL,
            },
            {
                "path": f"/odoo/action-stock.action_picking_tree_outgoing/{self.picking.id}",
                "name": "04_livrare_pret_zero.png",
                "click_btn": "button[name='button_validate']",
                "wait_after": MODAL,
            },
            {
                "path": "/odoo/action-base.ir_config_list_action?debug=1",
                "name": "05_parametri_sistem.png",
                "wait": ".o_list_view",
                "eval": SEARCH_PARAMS,
                "eval_wait": 2000,
            },
        ]

    def _capture(self, lang="ro_RO"):
        shots = self._shots()
        self.capture_screenshots(shots[:-1], lang=lang)
        # fără bara din dreapta-sus: în modul dezvoltator arată numele bazei de test
        self.capture_screenshots(shots[-1:], lang=lang, hide_systray=True)

    def test_capture_fise(self):
        self._capture()

    def test_capture_usage(self):
        self._capture(lang="en_US")

    def test_capture_gif(self):
        captions = {
            "post": {
                "ro_RO": "Factura de client cu marfă și fără comandă de vânzare nu se poate confirma",
                "en_US": "A customer invoice with goods and no sales order cannot be confirmed",
            },
            "validate": {
                "ro_RO": "Livrarea unei mărfi fără cost se oprește: prețul unitar este zero",
                "en_US": "Delivering goods without a cost stops: the unit price is zero",
            },
        }
        self.capture_gif(
            [
                {"path": f"/odoo/action-account.action_move_out_invoice_type/{self.out_invoice.id}"},
                {"caption": captions["post"]},
                {"click": "button[name='action_post']", "wait_after": MODAL, "hold": 2500},
                {"press": "Escape"},
                {"path": f"/odoo/action-stock.action_picking_tree_outgoing/{self.picking.id}"},
                {"caption": captions["validate"]},
                {"click": "button[name='button_validate']", "wait_after": MODAL, "hold": 2500},
            ],
            lang="en_US",
        )
