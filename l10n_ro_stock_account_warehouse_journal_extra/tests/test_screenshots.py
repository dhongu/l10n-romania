# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi de ecran pentru fișa punții „Jurnal de stoc pe depozit (OCA stock)" — în limba RO.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro,l10n_ro_stock_account_warehouse_journal_extra,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_stock_account_warehouse_journal_extra:TestWarehouseJournalExtraScreenshots --stop-after-init
import json
import unittest

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestWarehouseJournalExtraScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_account_warehouse_journal_extra"

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
        journal = env["account.journal"].create(
            {"name": "Stoc TW2", "code": "STW2", "type": "general", "company_id": company.id}
        )
        env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1).write(
            {"name": "Depozit București", "code": "BUC"}
        )
        cls.warehouse = env["stock.warehouse"].create(
            {"name": "Depozit Timișoara", "code": "TIM", "company_id": company.id}
        )
        cls.warehouse.l10n_ro_property_stock_journal_id = journal
        cls.act_warehouse = env.ref("stock.action_warehouse_form").id
        cls.act_modules = env.ref("base.open_module_tree").id

    def test_capture_fise(self):
        modules = [
            "l10n_ro_stock_account",
            "l10n_ro_stock_account_warehouse_journal",
            "l10n_ro_stock_account_warehouse_journal_extra",
        ]
        self.assertEqual(
            set(
                self.env["ir.module.module"]
                .search([("name", "in", modules), ("state", "=", "installed")])
                .mapped("name")
            ),
            set(modules),
        )
        self.capture_screenshots(
            [
                {
                    "url": f"action={self.act_modules}",
                    "name": "01_punte_instalata.png",
                    "wait": ".o_kanban_view, .o_list_view",
                    "eval": (
                        "() => odoo.__WOWL_DEBUG__.root.env.services.action.doAction({"
                        "type: 'ir.actions.act_window', res_model: 'ir.module.module', "
                        f"domain: {json.dumps([['name', 'in', modules]])}, views: [[false, 'list']], "
                        "name: 'Aplicații'}, {clearBreadcrumbs: true})"
                    ),
                    "eval_wait": 2500,
                    "settle": 2000,
                },
                {
                    "url": f"action={self.act_warehouse}&id={self.warehouse.id}&model=stock.warehouse&view_type=form",
                    "name": "02_depozit_jurnal_stoc.png",
                    "wait": ".o_form_view",
                    "highlight": ["div[name='l10n_ro_property_stock_journal_id']"],
                    "settle": 2000,
                },
            ]
        )
