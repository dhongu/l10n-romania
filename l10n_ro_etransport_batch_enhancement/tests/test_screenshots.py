# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Declarația eTransport pentru un lot de transferuri".
#
# Seedează: un lot cu două livrări către același client, cu transportator, greutăți cântărite
# și CMR pe lot; un lot cu greutățile încă nepreluate (avertismentul) și un lot cu UIT validat,
# gata de corecție, al cărui aviz de livrare poartă UIT-ul.
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_etransport_batch_enhancement,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_etransport_batch_enhancement:TestEtransportBatchScreenshots --stop-after-init
import unittest

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestEtransportBatchScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_etransport_batch_enhancement"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        company = cls.prepare_ro_company(name="Distribuție Demo SRL")
        env = cls.env
        ro = env.ref("base.ro")
        admin = env.ref("base.user_admin")
        # fusul orar al operatorului: altfel data planificată apare în UTC, cu ora de noapte
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id, "tz": "Europe/Bucharest"})
        for xmlid in ("stock.group_stock_user", "stock.group_stock_manager", "base.group_system"):
            grp = env.ref(xmlid, raise_if_not_found=False)
            if grp:
                admin.group_ids = [(4, grp.id)]

        company.l10n_ro_edi_access_token = "test-token"
        company.account_fiscal_country_id = ro

        cls.warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        # numele implicite ale companiei de test („company_1_data”) ar apărea pe fiecare transfer
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
        cls.transporter = env["res.partner"].create(
            {
                "name": "Rapid Cargo Transport",
                "vat": "8001011234567",
                "street": "Strada Mihai Viteazul 22",
                "city": "Caransebeș",
                "zip": "325400",
                "state_id": env.ref("base.RO_CS").id,
                "country_id": ro.id,
            }
        )
        product_vals = [
            {"name": "Laptop 15 inch", "weight": 2.0, "hs_code": "8471.30.00", "list_price": 3500.0},
            {"name": "Monitor 27 inch", "weight": 6.0, "hs_code": "8528.52", "list_price": 1200.0},
        ]
        # cu `l10n_ro_stock` instalat, greutatea netă declarată vine din „Greutate netă”, nu din „Masă”
        if "l10n_ro_net_weight" in env["product.product"]._fields:
            product_vals[0]["l10n_ro_net_weight"] = 1.8
            product_vals[1]["l10n_ro_net_weight"] = 5.2
        cls.laptop, cls.monitor = env["product.product"].create([dict(vals, type="consu") for vals in product_vals])

        # 1. Lotul complet: două livrări, transportator, greutăți cântărite, CMR pe lot (pașii 1–5)
        cls.batch = cls._create_batch([[(cls.laptop, 10)], [(cls.monitor, 4)]])
        cls.batch.write({"l10n_ro_shipping_weights": True, "total_net_weight": 40.0, "total_gross_weight": 46.0})
        cls.batch.l10n_ro_compute_weight_lines()
        cls.batch.l10n_ro_distribute_weights()
        cls.batch.picking_ids.l10n_ro_etransport_add_default_documents()
        env["l10n.ro.etransport.document"].create(
            {
                "batch_id": cls.batch.id,
                "document_type": "10",
                "name": "4471",
                "date": cls.batch.scheduled_date.date(),
            }
        )

        # 2. Lotul cu greutăți bifate, dar cu liniile încă nepreluate: avertismentul (pasul 4)
        cls.batch_warning = cls._create_batch([[(cls.laptop, 5)], [(cls.monitor, 2)]])
        cls.batch_warning.l10n_ro_shipping_weights = True

        # 3. Lotul cu UIT validat, gata de corecție; avizul lotului afișează UIT-ul (pașii 6 și 7)
        cls.batch_amend = cls._create_batch([[(cls.laptop, 3)], [(cls.monitor, 1)]])
        cls.batch_amend._l10n_ro_edi_stock_create_document_stock_validated(
            {"l10n_ro_edi_stock_load_id": 1, "l10n_ro_edi_stock_uit": "ACDEFHJKLMNPQR56", "raw_xml": "<eTransport/>"}
        )

        env.flush_all()

    @classmethod
    def _create_batch(cls, deliveries):
        """Lot în desfășurare, cu livrările confirmate și datele declarației completate."""
        env = cls.env
        customers = env.ref("stock.stock_location_customers")
        pickings = env["stock.picking"]
        for lines in deliveries:
            if "sale_line_id" in env["stock.move"]._fields:
                # din comandă de vânzare, ca avizul lotului să aibă prețuri și valori
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
            else:
                picking = env["stock.picking"].create(
                    {
                        "partner_id": cls.customer.id,
                        "picking_type_id": cls.warehouse.out_type_id.id,
                        "location_id": cls.warehouse.lot_stock_id.id,
                        "location_dest_id": customers.id,
                        "move_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": product.id,
                                    "product_uom_qty": qty,
                                    "uom_id": product.uom_id.id,
                                    "location_id": cls.warehouse.lot_stock_id.id,
                                    "location_dest_id": customers.id,
                                },
                            )
                            for product, qty in lines
                        ],
                    }
                )
                picking.action_confirm()
            for move in picking.move_ids:
                move.quantity = move.product_uom_qty
            pickings |= picking
        batch = env["stock.picking.batch"].create(
            {
                "picking_ids": [(6, 0, pickings.ids)],
                "picking_type_id": cls.warehouse.out_type_id.id,
                "company_id": cls.warehouse.company_id.id,
                "l10n_ro_edi_stock_required": True,
            }
        )
        batch.action_confirm()
        batch.write(
            {
                # transportatorul se scrie pe lot și coboară pe livrări (inverse)
                "l10n_ro_transport_partner_id": cls.transporter.id,
                "l10n_ro_edi_stock_operation_type": "30",
                "l10n_ro_edi_stock_operation_scope": "101",
                "l10n_ro_edi_stock_vehicle_number": "BV 12 RCT",
                "l10n_ro_edi_stock_start_loc_type": "location",
                "l10n_ro_edi_stock_end_loc_type": "location",
            }
        )
        return batch

    @staticmethod
    def _scroll_to(selector, block="center"):
        """JS care așteaptă elementul (tab-ul se randează după click) și îl aduce în ecran."""
        return (
            "(async () => {"
            " for (let i = 0; i < 40; i++) {"
            f'  const e = document.querySelector("{selector}");'
            f"  if (e) {{ e.scrollIntoView({{block: '{block}'}}); return; }}"
            "  await new Promise(r => setTimeout(r, 200));"
            " }"
            "})()"
        )

    def _batch_url(self, batch):
        action = self.env.ref("stock.stock_picking_batch_action")
        return f"action={action.id}&id={batch.id}&model=stock.picking.batch&view_type=form"

    # ------------------------------------------------------------------
    def test_capture_fise(self):
        self.capture_screenshots(
            [
                # 1. Lotul: eTransport necesar, metoda de livrare și transportatorul
                {
                    "url": self._batch_url(self.batch),
                    "name": "01_lot_transportator.png",
                    "wait": ".o_form_view",
                    "wait_after": "div[name='l10n_ro_transport_partner_id']",
                    # responsabilul vine din utilizatorul de test, irelevant aici
                    "hide_fields": ["user_id"],
                    "highlight": [
                        "div[name='l10n_ro_edi_stock_required']",
                        "div[name='l10n_ro_transport_partner_id']",
                    ],
                    "settle": 2500,
                },
                # 2. Datele declarației (tab-ul eTransport) și butonul de trimitere
                {
                    "url": self._batch_url(self.batch),
                    "name": "02_date_declaratie_lot.png",
                    "wait": ".o_form_view",
                    "click_btn": ".nav-link:has-text('eTransport') >> nth=0",
                    "wait_after": "div[name='l10n_ro_edi_stock_operation_type']",
                    "hide_fields": ["user_id"],
                    "highlight": [
                        "div[name='l10n_ro_edi_stock_operation_type']",
                        "div[name='l10n_ro_edi_stock_vehicle_number']",
                        "div[name='l10n_ro_etransport_post_outage']",
                        "button[name='action_l10n_ro_edi_stock_send_etransport'] >> visible=true",
                    ],
                    "settle": 2500,
                },
                # 3. Greutățile cântărite, repartizate pe liniile ambelor livrări
                {
                    "url": self._batch_url(self.batch),
                    "name": "03_greutati_lot.png",
                    "wait": ".o_form_view",
                    "click_btn": ".nav-link:has-text('eTransport') >> nth=0",
                    "wait_after": "div[name='l10n_ro_edi_stock_operation_type']",
                    "eval": self._scroll_to("div[name='l10n_ro_shipping_weight_lines']"),
                    "highlight": [
                        "div[name='total_net_weight']",
                        "div[name='total_gross_weight']",
                        "button[name='l10n_ro_compute_weight_lines']",
                        "button[name='l10n_ro_distribute_weights']",
                    ],
                    "settle": 2500,
                },
                # 4. Avertismentul: mișcări ale lotului fără linie de greutate
                {
                    "url": self._batch_url(self.batch_warning),
                    "name": "04_avertisment_greutati.png",
                    "wait": ".o_form_view",
                    "click_btn": ".nav-link:has-text('eTransport') >> nth=0",
                    "wait_after": "div[name='l10n_ro_shipping_weight_lines_warning']",
                    "eval": self._scroll_to("div[name='l10n_ro_shipping_weight_lines_warning']"),
                    "highlight": [
                        ".alert-danger:has(div[name='l10n_ro_shipping_weight_lines_warning'])",
                        "button[name='l10n_ro_compute_weight_lines']",
                    ],
                    "settle": 2500,
                },
                # 5. Documentele însoțitoare: CMR-ul lotului și avizele livrărilor
                {
                    "url": self._batch_url(self.batch),
                    "name": "05_documente_lot.png",
                    "wait": ".o_form_view",
                    "click_btn": ".nav-link:has-text('eTransport') >> nth=0",
                    "wait_after": "div[name='l10n_ro_etransport_document_ids']",
                    "eval": self._scroll_to("div[name='l10n_ro_etransport_all_document_ids']"),
                    "highlight": [
                        "div[name='l10n_ro_etransport_document_ids']",
                        "div[name='l10n_ro_etransport_all_document_ids']",
                    ],
                    "settle": 2500,
                },
                # 6. Corecția: lotul cu UIT validat
                {
                    "url": self._batch_url(self.batch_amend),
                    "name": "06_corectie_uit_lot.png",
                    "wait": ".o_form_view",
                    "click_btn": ".nav-link:has-text('Documente eTransport')",
                    "wait_after": "div[name='l10n_ro_edi_stock_document_ids']",
                    "hide_fields": ["user_id"],
                    "highlight": ["button:has-text('Modificați eTransport')"],
                    "settle": 2500,
                },
                # 7. Avizul de livrare al lotului, cu UIT-ul validat
                self.report_shot(
                    "l10n_ro_stock_picking_batch_report.report_batch_delivery",
                    self.batch_amend,
                    "07_aviz_lot_uit.png",
                    highlight="span:has(> strong:has-text('UIT:'))",
                ),
            ],
            hide_systray=True,
        )
