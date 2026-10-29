# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Avizul de însoțire a mărfii pentru un lot de transferuri".
#
# Seedează un lot în desfășurare cu două livrări din comenzi de vânzare către același client;
# laptopul apare în ambele, ca avizul să arate cumularea pe produs.
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_stock_picking_batch_report,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_stock_picking_batch_report:TestBatchReportScreenshots --stop-after-init
import unittest

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestBatchReportScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_picking_batch_report"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        if "sale.order" not in cls.env:
            # prețurile de pe aviz vin din comenzi: fără `sale` captura nu are valori
            raise unittest.SkipTest("modulul sale nu e instalat")
        company = cls.prepare_ro_company(name="Distribuție Demo SRL")
        env = cls.env
        ro = env.ref("base.ro")
        admin = env.ref("base.user_admin")
        # fusul orar al operatorului: altfel data planificată apare în UTC, cu ora de noapte
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id, "tz": "Europe/Bucharest"})
        # `uom.group_uom`: coloana U/M de pe aviz, cerută de formularul 14-3-6A
        for xmlid in (
            "stock.group_stock_user",
            "stock.group_stock_manager",
            "sales_team.group_sale_salesman",
            "uom.group_uom",
        ):
            grp = env.ref(xmlid, raise_if_not_found=False)
            if grp:
                admin.group_ids = [(4, grp.id)]

        cls.warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        # numele implicite ale companiei de test („company_1_data”) ar apărea pe aviz
        cls.warehouse.write({"name": "Depozit Central", "code": "DC", "partner_id": company.partner_id.id})
        cls.warehouse.out_type_id.name = "Livrări"

        cls.customer = env["res.partner"].create(
            {
                "name": "Magazinul Tehnic SRL",
                "vat": "RO1234567897",
                "street": "Strada General Traian Moșoiu 24",
                "city": "Brașov",
                "zip": "500024",
                "state_id": env.ref("base.RO_BV").id,
                "country_id": ro.id,
            }
        )
        cls.laptop, cls.monitor = env["product.product"].create(
            [
                {"name": "Laptop 15 inch", "type": "consu", "list_price": 3500.0},
                {"name": "Monitor 27 inch", "type": "consu", "list_price": 1200.0},
            ]
        )

        # laptopul e în ambele livrări: pe aviz apare o singură linie, cu 15 bucăți
        cls.batch = cls._create_batch([[(cls.laptop, 10), (cls.monitor, 4)], [(cls.laptop, 5)]])
        # delegatul și mijlocul de transport ajung pe aviz de pe prima livrare din lot
        delegate = env["res.partner"].create({"name": "Ion Popescu", "parent_id": cls.customer.id})
        # „prima” livrare e cea din ordinea modelului (`stock.picking._order`), ca în raport
        first = env["stock.picking"].search([("batch_id", "=", cls.batch.id)], limit=1)
        first.write({"delegate_id": delegate.id, "mean_transp": "BV 12 RCT"})
        env.flush_all()

    @classmethod
    def _create_batch(cls, deliveries):
        """Lot în desfășurare, cu livrările confirmate din comenzi de vânzare."""
        env = cls.env
        pickings = env["stock.picking"]
        for lines in deliveries:
            order = (
                env["sale.order"]
                .sudo()
                .create(
                    {
                        "partner_id": cls.customer.id,
                        "company_id": cls.warehouse.company_id.id,
                        "warehouse_id": cls.warehouse.id,
                        "order_line": [
                            (0, 0, {"product_id": product.id, "product_uom_qty": qty}) for product, qty in lines
                        ],
                    }
                )
            )
            order.action_confirm()
            picking = order.picking_ids.sudo(False)
            for move in picking.move_ids:
                move.quantity = move.product_uom_qty
            pickings |= picking
        batch = env["stock.picking.batch"].create(
            {
                "picking_ids": [(6, 0, pickings.ids)],
                "picking_type_id": cls.warehouse.out_type_id.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        batch.action_confirm()
        return batch

    def _batch_url(self, batch):
        action = self.env.ref("stock.stock_picking_batch_action")
        return f"action={action.id}&id={batch.id}&model=stock.picking.batch&view_type=form"

    # ------------------------------------------------------------------
    def test_capture_fise(self):
        self.capture_screenshots(
            [
                # 1. Lotul cu livrările care pleacă împreună
                {
                    "url": self._batch_url(self.batch),
                    "name": "01_lot_livrari.png",
                    "wait": ".o_form_view",
                    "wait_after": "div[name='move_ids'] .o_data_row",
                    # responsabilul vine din utilizatorul de test, iar bifa eTransport din alt modul
                    "hide_fields": ["user_id", "l10n_ro_edi_stock_required"],
                    # laptopul vine din ambele livrări: pe aviz devine o singură linie
                    "highlight": [
                        ".o_data_row:has-text('Laptop 15 inch') >> nth=0 >> td.o_data_cell >> nth=1",
                        ".o_data_row:has-text('Laptop 15 inch') >> nth=1 >> td.o_data_cell >> nth=1",
                    ],
                    "settle": 2500,
                },
                # 2. Tipărirea avizului din rotița de acțiuni
                {
                    "url": self._batch_url(self.batch),
                    "name": "02_tiparire_aviz.png",
                    "wait": ".o_form_view",
                    "click_btn": ".o_cp_action_menus button:has(i[data-icon='more_vert'])",
                    "wait_after": ".o-dropdown--menu",
                    "eval": (
                        "(async () => {"
                        " for (let i = 0; i < 40; i++) {"
                        "  const e = document.querySelector('.o-dropdown--menu button:has(i[data-icon=\"print\"])');"
                        "  if (e) { e.click(); return; }"
                        "  await new Promise(r => setTimeout(r, 200));"
                        " }"
                        "})()"
                    ),
                    "eval_wait": 1500,
                    "hide_fields": ["user_id", "l10n_ro_edi_stock_required"],
                    "highlight": [
                        ".o_cp_action_menus button:has(i[data-icon='more_vert'])",
                        '.o-dropdown--menu button:has(i[data-icon="print"])',
                        ".o-dropdown-item:text-is('Aviz')",
                    ],
                    "settle": 2000,
                },
                # 3. Avizul lotului: produsele cumulate, prețurile din comenzi
                self.report_shot(
                    "l10n_ro_stock_picking_batch_report.report_batch_delivery",
                    self.batch,
                    "03_aviz_lot.png",
                    highlight=["div[name='address']", "table.table-sm", "td:has(> div > span:text-is('Delegat:'))"],
                ),
            ],
            hide_systray=True,
        )
