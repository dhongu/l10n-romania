# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Declarația eTransport completă și corectă din transfer".
#
# Seedează: setările UIT ale companiei, un produs cu cod SH, o livrare cu transportator,
# una cu greutăți măsurate și documente însoțitoare, una blocată (produs fără cod SH)
# și una cu UIT validat, gata de corecție.
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_etransport_enhancement,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_etransport_enhancement:TestEtransportScreenshots --stop-after-init
import unittest
from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None

UPLOAD_PATCH = "odoo.addons.l10n_ro_edi_stock.models.etransport_api.ETransportAPI.upload_data"


@tagged("-at_install", "post_install", "fise_screenshots")
class TestEtransportScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_etransport_enhancement"

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

        company.write(
            {
                "l10n_ro_edi_access_token": "test-token",
                "l10n_ro_etransport_get_order_value": True,
            }
        )
        # starea declarației și tab-ul eTransport există doar pentru țara fiscală RO
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
        cls.laptop = env["product.product"].create(
            {"name": "Laptop 15 inch", "type": "consu", "weight": 2.0, "hs_code": "8471.30.00"}
        )
        cls.monitor = env["product.product"].create(
            {"name": "Monitor 27 inch", "type": "consu", "weight": 6.0, "hs_code": "8528.52"}
        )
        cls.cablu = env["product.product"].create({"name": "Cablu HDMI 2 m", "type": "consu", "weight": 0.2})

        # 1. Livrarea obișnuită: transportator, operațiune 30, vehicul (pașii 3 și 4)
        cls.picking = cls._create_delivery([(cls.laptop, 10), (cls.monitor, 4)])

        # 2. Livrarea cântărită: totalurile de pe cântar repartizate pe linii,
        #    plus documentele însoțitoare (pașii 5 și 6)
        cls.picking_weights = cls._create_delivery([(cls.laptop, 10), (cls.monitor, 4)])
        cls.picking_weights.write(
            {"l10n_ro_shipping_weights": True, "total_net_weight": 44.0, "total_gross_weight": 52.0}
        )
        cls.picking_weights.l10n_ro_compute_weight_lines()
        cls.picking_weights.l10n_ro_distribute_weights()
        cls.picking_weights.l10n_ro_etransport_add_default_documents()
        env["l10n.ro.etransport.document"].create(
            {
                "picking_id": cls.picking_weights.id,
                "document_type": "10",
                "name": "CMR 4471",
                "date": cls.picking_weights.scheduled_date.date(),
            }
        )

        # 3. Livrarea blocată: produsul fără cod SH oprește declarația (pasul 7)
        cls.picking_blocked = cls._create_delivery([(cls.laptop, 2), (cls.cablu, 20)])
        with patch(UPLOAD_PATCH) as upload:
            # mesajul de eroare se salvează pe document în limba de la trimitere
            cls.picking_blocked.with_context(lang="ro_RO")._l10n_ro_edi_stock_send_etransport_document("send")
            assert not upload.called, "declarația fără cod SH nu trebuie să ajungă la ANAF"

        # 4. Livrarea cu UIT validat, gata de corecție (pasul 8)
        cls.picking_amend = cls._create_delivery([(cls.laptop, 5)])
        cls.picking_amend._l10n_ro_edi_stock_create_document_stock_validated(
            {"l10n_ro_edi_stock_load_id": 1, "l10n_ro_edi_stock_uit": "ACDEFHJKLMNPQR34", "raw_xml": "<eTransport/>"}
        )

        env.flush_all()

    @classmethod
    def _create_delivery(cls, lines):
        """Livrare confirmată, cu cantitățile pregătite și datele declarației completate."""
        env = cls.env
        customers = env.ref("stock.stock_location_customers")
        picking = env["stock.picking"].create(
            {
                "partner_id": cls.customer.id,
                "picking_type_id": cls.warehouse.out_type_id.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": customers.id,
                "l10n_ro_edi_stock_required": True,
                "l10n_ro_transport_partner_id": cls.transporter.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom": product.uom_id.id,
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
        picking.write(
            {
                "l10n_ro_edi_stock_operation_type": "30",
                "l10n_ro_edi_stock_operation_scope": "101",
                "l10n_ro_edi_stock_vehicle_number": "BV 12 RCT",
                "l10n_ro_edi_stock_start_loc_type": "location",
                "l10n_ro_edi_stock_end_loc_type": "location",
            }
        )
        return picking

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

    def _picking_url(self, picking):
        action = self.env.ref("stock.action_picking_tree_all")
        return f"action={action.id}&id={picking.id}&model=stock.picking&view_type=form"

    # ------------------------------------------------------------------
    def test_capture_fise(self):
        settings_action = self.env.ref("stock.action_stock_config_settings")
        self.capture_screenshots(
            [
                # 1. Setările UIT din Inventar
                {
                    "url": f"action={settings_action.id}",
                    "name": "01_setari_uit.png",
                    "wait": "div[name='uit_settings'], #l10n_ro_etransport_timeout",
                    "timeout": 60000,
                    "eval": "document.querySelector('#l10n_ro_etransport_get_order_value')"
                    "?.closest('.o_setting_container, .o_settings_container, div[name=uit_settings]')"
                    "?.scrollIntoView({block: 'center'})",
                    "highlight": ["#l10n_ro_etransport_get_order_value", "#l10n_ro_etransport_timeout"],
                    "settle": 2500,
                },
                # 2. Produsul cu codul SH (tab-ul Inventar)
                {
                    "url": (f"id={self.laptop.product_tmpl_id.id}&model=product.template&view_type=form"),
                    "name": "02_produs_cod_sh.png",
                    "wait": ".o_form_view",
                    "click_btn": "a.nav-link:has-text('Inventar')",
                    "wait_after": "div[name='hs_code']",
                    # responsabilul vine din utilizatorul de test, irelevant aici
                    "hide_fields": ["responsible_id"],
                    # celula valorii (cea mai interioară), ca bulina să nu fie tăiată și să nu acopere cifrele
                    "highlight": [
                        ".o_cell:has(div[name='weight']) >> nth=-1",
                        ".o_cell:has(div[name='hs_code']) >> nth=-1",
                    ],
                    "settle": 2000,
                },
                # 3. Livrarea: eTransport necesar și transportatorul (Informații suplimentare)
                {
                    "url": self._picking_url(self.picking),
                    "name": "03_transportator.png",
                    "wait": ".o_form_view",
                    "click_btn": "a.nav-link:has-text('Informații suplimentare')",
                    "wait_after": "div[name='l10n_ro_transport_partner_id']",
                    # responsabilul și lotul vin din datele de test, irelevante aici
                    "hide_fields": ["user_id", "batch_id"],
                    "highlight": [
                        "div[name='l10n_ro_edi_stock_required'] >> visible=true",
                        "div[name='l10n_ro_transport_partner_id'] >> visible=true",
                    ],
                    "settle": 2500,
                },
                # 4. Datele declarației (tab-ul eTransport) și butonul de trimitere
                {
                    "url": self._picking_url(self.picking),
                    "name": "04_date_declaratie.png",
                    "wait": ".o_form_view",
                    "click_btn": "a.nav-link:has-text('eTransport')",
                    "wait_after": "div[name='l10n_ro_edi_stock_operation_type']",
                    "highlight": [
                        "div[name='l10n_ro_edi_stock_operation_type']",
                        "div[name='l10n_ro_edi_stock_vehicle_number']",
                        "div[name='l10n_ro_etransport_post_outage']",
                        "button[name='action_l10n_ro_edi_stock_send_etransport'] >> visible=true",
                    ],
                    "settle": 2500,
                },
                # 5. Greutățile măsurate, repartizate pe linii
                {
                    "url": self._picking_url(self.picking_weights),
                    "name": "05_greutati_masurate.png",
                    "wait": ".o_form_view",
                    "click_btn": "a.nav-link:has-text('eTransport')",
                    "wait_after": "div[name='l10n_ro_edi_stock_operation_type']",
                    "eval": self._scroll_to("div[name='l10n_ro_shipping_weight_lines']"),
                    "highlight": [
                        "div[name='total_net_weight']",
                        "div[name='total_gross_weight']",
                        "button[name='l10n_ro_distribute_weights']",
                    ],
                    "settle": 2500,
                },
                # 6. Documentele însoțitoare
                {
                    "url": self._picking_url(self.picking_weights),
                    "name": "06_documente_insotitoare.png",
                    "wait": ".o_form_view",
                    "click_btn": "a.nav-link:has-text('eTransport')",
                    "wait_after": "div[name='l10n_ro_edi_stock_operation_type']",
                    "eval": self._scroll_to("button[name='l10n_ro_etransport_add_default_documents']"),
                    "highlight": [
                        "div[name='l10n_ro_etransport_document_ids']",
                        "button[name='l10n_ro_etransport_add_default_documents']",
                    ],
                    "settle": 2500,
                },
                # 7. Declarația oprită: produsul fără cod SH
                {
                    "url": self._picking_url(self.picking_blocked),
                    "name": "07_blocaj_cod_sh.png",
                    "wait": ".o_form_view",
                    "click_btn": "a.nav-link:has-text('Documente eTransport')",
                    "wait_after": "div[name='l10n_ro_edi_stock_document_ids']",
                    "eval": (
                        "(async () => {"
                        " for (let i = 0; i < 40; i++) {"
                        "  const e = document.querySelector(\"td[name='state'] i, td[name='state'] .fa\");"
                        "  if (e) { e.click(); return; }"
                        "  await new Promise(r => setTimeout(r, 200));"
                        " }"
                        "})()"
                    ),
                    "eval_wait": 1500,
                    "settle": 2500,
                },
                # 8. Corecția: transferul cu UIT validat
                {
                    "url": self._picking_url(self.picking_amend),
                    "name": "08_corectie_uit.png",
                    "wait": ".o_form_view",
                    "click_btn": "a.nav-link:has-text('Documente eTransport')",
                    "wait_after": "div[name='l10n_ro_edi_stock_document_ids']",
                    "highlight": ["button:has-text('Modificați eTransport')"],
                    "settle": 2500,
                },
            ],
            hide_systray=True,
        )
