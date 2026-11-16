# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi de ecran pentru fișa „Jurnal de stoc pe depozit" — generate în timpul testelor, în limba RO.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_stock_account_warehouse_journal,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_stock_account_warehouse_journal:TestWarehouseJournalScreenshots --stop-after-init
import unittest

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestWarehouseJournalScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_account_warehouse_journal"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Demo Depozite SRL")
        env = cls.env
        company = env.company
        env.ref("base.user_admin").write({"company_ids": [(4, company.id)], "company_id": company.id})

        cls.journal = env["account.journal"].create(
            {"name": "Stoc TW2", "code": "STW2", "type": "general", "company_id": company.id}
        )
        env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1).write(
            {"name": "Depozit București", "code": "BUC"}
        )
        cls.warehouse = env["stock.warehouse"].create(
            {"name": "Depozit Timișoara", "code": "TIM", "company_id": company.id}
        )
        cls.warehouse.l10n_ro_property_stock_journal_id = cls.journal

        def account(prefix, fallback_type):
            return env["account.account"].search(
                [("code", "=like", prefix + "%"), ("company_ids", "in", [company.id])], order="code", limit=1
            ) or env["account.account"].search(
                [("account_type", "=", fallback_type), ("company_ids", "in", [company.id])], limit=1
            )

        acc_stock = account("371", "asset_current")
        acc_adjust = account("607", "expense")
        categ = env["product.category"].create(
            {
                "name": "Mărfuri",
                "property_cost_method": "average",
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": acc_stock.id,
            }
        )
        # contrapartida notei de inventar: contul locației virtuale
        env["stock.location"].search([("usage", "=", "inventory"), ("company_id", "in", [company.id, False])]).write(
            {"valuation_account_id": acc_adjust.id}
        )
        cls.product = env["product.product"].create(
            {
                "name": "Tablă 2mm",
                "is_storable": True,
                "categ_id": categ.id,
                "standard_price": 10.0,
                "taxes_id": [Command.clear()],
            }
        )
        cls.quant = (
            env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": cls.product.id,
                    "location_id": cls.warehouse.lot_stock_id.id,
                    "inventory_quantity": 5,
                }
            )
        )
        cls.quant.with_context(inventory_name="Inventariere 10.11").action_apply_inventory()
        cls.move = env["stock.move"].search(
            [("product_id", "=", cls.product.id), ("location_dest_id", "=", cls.warehouse.lot_stock_id.id)],
            limit=1,
        )
        cls.entry = cls.move.account_move_id
        cls.act_inventory = env.ref("stock.action_view_inventory_tree").id
        cls.act_warehouse = env.ref("stock.action_warehouse_form").id

    def test_capture_fise(self):
        self.assertTrue(self.entry, "ajustarea de inventar trebuie să genereze notă")
        self.assertEqual(self.entry.journal_id, self.journal)
        self.capture_screenshots(
            [
                {
                    "url": f"action={self.act_warehouse}&id={self.warehouse.id}&model=stock.warehouse&view_type=form",
                    "name": "01_depozit_jurnal_stoc.png",
                    "wait": ".o_form_view",
                    "highlight": ["div[name='l10n_ro_property_stock_journal_id']"],
                    "settle": 2000,
                },
                {
                    "url": f"action={self.act_inventory}",
                    "name": "02_ajustare_inventar.png",
                    "wait": ".o_list_view",
                    "settle": 2000,
                },
                self.account_move_shot(self.entry, "03_nota_in_jurnalul_depozitului.png"),
            ]
        )
