# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „NIR, aviz de însoțire, bon de consum și notă de transfer".
#
# Seedează: o locație de magazin cu listă de prețuri, o recepție dintr-o comandă de achiziție
# (cu delegat și mijloc de transport), o recepție în cutii de 13 kg pe `stock.propagate_uom = 1`,
# o livrare marcată ca aviz, un consum și un transfer intern, plus un raport cumulativ.
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_stock_picking_report,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_stock_picking_report:TestPickingReportScreenshots --stop-after-init
import unittest

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestPickingReportScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_picking_report"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Depozit Demo SRL")
        env = cls.env
        company = env.company
        admin = env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        for xmlid in (
            "stock.group_stock_user",
            "stock.group_stock_manager",
            "stock.group_stock_multi_locations",
            "uom.group_uom",  # fără el, coloana U/M nu se tipărește pe niciun raport
            "purchase.group_purchase_user",
        ):
            grp = env.ref(xmlid, raise_if_not_found=False)
            if grp:
                admin.group_ids = [(4, grp.id)]

        # Cazul cu unități de ambalare are sens doar cu propagarea unității activă;
        # implicit Odoo convertește mișcarea în unitatea de referință a produsului.
        env["ir.config_parameter"].sudo().set_param("stock.propagate_uom", "1")

        cls.warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        if not cls.warehouse:
            cls.warehouse = env["stock.warehouse"].create(
                {"name": "Depozit Central", "code": "DC", "company_id": company.id}
            )
        cls.warehouse.write({"name": "Depozit Central", "code": "DC"})
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.stock_location.name = "Magazie materiale"

        cls.picking_type_in = cls.warehouse.in_type_id
        cls.picking_type_out = cls.warehouse.out_type_id
        cls.picking_type_int = cls.warehouse.int_type_id

        # Locația de magazin, cu lista de prețuri care alimentează „Preț vânzare" de pe NIR
        cls.pricelist_magazin = env["product.pricelist"].create(
            {
                "name": "Preț raft magazin",
                "currency_id": company.currency_id.id,
                "company_id": company.id,
            }
        )
        cls.gestionar = env["res.users"].create(
            {
                "name": "Elena Marinescu",
                "login": "elena.marinescu",
                "company_ids": [(6, 0, [company.id])],
                "company_id": company.id,
            }
        )
        cls.location_magazin = env["stock.location"].create(
            {
                "name": "Magazin de prezentare",
                "usage": "internal",
                "location_id": cls.warehouse.view_location_id.id,
                "company_id": company.id,
                "store_pricelist_id": cls.pricelist_magazin.id,
                "user_id": cls.gestionar.id,
            }
        )

        country_ro = env.ref("base.ro")
        cls.supplier = env["res.partner"].create(
            {
                "name": "Moara Bănățeană SRL",
                "is_company": True,
                "country_id": country_ro.id,
                "street": "Calea Lugojului 45",
                "city": "Timișoara",
                "zip": "300001",
            }
        )
        cls.customer = env["res.partner"].create(
            {
                "name": "Brutăria Aurora SRL",
                "is_company": True,
                "country_id": country_ro.id,
                "street": "Str. Morii 8",
                "city": "Arad",
                "zip": "310001",
            }
        )
        cls.delegat = env["res.partner"].create(
            {
                "name": "Andrei Munteanu",
                "is_company": False,
                "function": "Șofer",
                "mean_transp": "TM 04 MBS",
            }
        )

        cls.tax_purchase = cls.company_data["default_tax_purchase"]
        cls.tax_sale = cls.company_data["default_tax_sale"]

        uom_kg = env.ref("uom.product_uom_kgm")
        cls.faina = env["product.product"].create(
            {
                "name": "Făină albă tip 000",
                "is_storable": True,
                "uom_id": uom_kg.id,
                "standard_price": 2.50,
                "list_price": 4.20,
                "supplier_taxes_id": [(6, 0, cls.tax_purchase.ids)],
                "taxes_id": [(6, 0, cls.tax_sale.ids)],
            }
        )
        cls.zahar = env["product.product"].create(
            {
                "name": "Zahăr tos",
                "is_storable": True,
                "uom_id": uom_kg.id,
                "standard_price": 2.90,
                "list_price": 4.50,
                "supplier_taxes_id": [(6, 0, cls.tax_purchase.ids)],
                "taxes_id": [(6, 0, cls.tax_sale.ids)],
            }
        )
        # prețul de raft: pe recepția în magazin, NIR-ul trebuie să îl ia de aici,
        # nu din prețul de listă al produsului
        env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist_magazin.id,
                "applied_on": "0_product_variant",
                "product_id": cls.faina.id,
                "compute_price": "fixed",
                "fixed_price": 5.90,
            }
        )
        cls.uom_cutie = env["uom.uom"].create(
            {
                "name": "Cutie 13 kg",
                "relative_uom_id": cls.zahar.uom_id.id,
                "relative_factor": 13.0,
            }
        )

        # 1. Recepție obișnuită, în kilograme, într-o gestiune de magazin (pașii 1–5)
        cls.picking_nir = cls._receive_purchase(
            cls.faina,
            200.0,
            3.10,
            cls.faina.uom_id,
            location_dest=cls.location_magazin,
            partner_ref="F 2026-4417",
        )
        cls.picking_nir.write({"delegate_id": cls.delegat.id, "mean_transp": "TM 04 MBS"})

        # 2. Recepție în cutii de 13 kg: 1.344 cutii × 37,70 lei = 50.668,80 lei (pasul 6)
        cls.picking_cutii = cls._receive_purchase(cls.zahar, 1344.0, 37.70, cls.uom_cutie, partner_ref="F 2026-4418")
        cls.picking_cutii.write({"delegate_id": cls.delegat.id, "mean_transp": "TM 04 MBS"})

        # 3. Livrare marcată ca aviz de însoțire (pasul 7)
        cls.picking_aviz = cls._make_internal_picking(
            cls.picking_type_out,
            cls.faina,
            50.0,
            cls.faina.uom_id,
            partner=cls.customer,
            location_dest=env.ref("stock.stock_location_customers"),
        )
        cls.picking_aviz.write({"delegate_id": cls.delegat.id, "mean_transp": "TM 04 MBS"})
        if "l10n_ro_notice" in env["stock.picking"]._fields:
            cls.picking_aviz.l10n_ro_notice = True

        # 4. Consum din magazie (pasul 8) și transfer între gestiuni (pasul 9)
        cls.picking_consum = cls._make_internal_picking(
            cls.picking_type_int, cls.faina, 30.0, cls.faina.uom_id, location_dest=cls.location_magazin
        )
        cls.picking_transfer = cls._make_internal_picking(
            cls.picking_type_int, cls.faina, 45.0, cls.faina.uom_id, location_dest=cls.location_magazin
        )

        # 5. Raportul cumulativ pe recepții (pasul 10)
        cls.report_cumulativ = env.ref("l10n_ro_stock_picking_report.action_report_c_recep_sale_price")
        cls.cumulative = env["stock.picking.cumulative"].create(
            {
                "picking_type_id": cls.picking_type_in.id,
                "report_id": cls.report_cumulativ.id,
            }
        )
        cls.cumulative.move_ids = [(6, 0, (cls.picking_nir | cls.picking_cutii).move_ids.ids)]

        env.flush_all()

    # ------------------------------------------------------------------
    # Ajutoare de seed
    # ------------------------------------------------------------------
    @classmethod
    def _receive_purchase(cls, product, qty, price_unit, uom, location_dest=None, partner_ref=None):
        """Comandă de achiziție confirmată + recepția ei validată.

        `partner_ref` ajunge în `origin`-ul recepției (vezi `models/purchase.py`) și de
        acolo în rubrica „conform documentului nr." de pe NIR.
        """
        purchase = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                "partner_ref": partner_ref or False,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_qty": qty,
                            "product_uom_id": uom.id,
                            "price_unit": price_unit,
                            "tax_ids": [(6, 0, cls.tax_purchase.ids)],
                        },
                    )
                ],
            }
        )
        purchase.button_confirm()
        picking = purchase.picking_ids[:1]
        if location_dest:
            # destinația trebuie schimbată ÎNAINTE de validare: prețul de vânzare se
            # îngheață în `_action_done` din lista de prețuri a locației de destinație
            picking.location_dest_id = location_dest.id
            picking.move_ids.location_dest_id = location_dest.id
            picking.move_ids.move_line_ids.location_dest_id = location_dest.id
        for move in picking.move_ids:
            move.move_line_ids.quantity = move.product_uom_qty
        picking.move_ids.picked = True
        picking._action_done()
        return picking

    @classmethod
    def _make_internal_picking(cls, picking_type, product, qty, uom, partner=None, location_dest=None):
        """Transfer validat (livrare, consum sau transfer intern)."""
        vals = {
            "picking_type_id": picking_type.id,
            "location_id": cls.stock_location.id,
            "location_dest_id": (location_dest or picking_type.default_location_dest_id).id,
        }
        if partner:
            vals["partner_id"] = partner.id
        picking = cls.env["stock.picking"].create(vals)
        cls.env["stock.move"].create(
            {
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": uom.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        picking.action_confirm()
        for move in picking.move_ids:
            move.move_line_ids.quantity = move.product_uom_qty
        picking.move_ids.picked = True
        picking._action_done()
        return picking

    # ------------------------------------------------------------------
    def test_capture_fise(self):
        action_cumulativ = self.env.ref("l10n_ro_stock_picking_report.action_stock_picking_cumulative")
        act_picking = self.env.ref("stock.action_picking_tree_all")
        self.capture_screenshots(
            [
                # 1. Locația de gestiune, cu lista de prețuri și managerul
                {
                    "url": f"id={self.location_magazin.id}&model=stock.location&view_type=form",
                    "name": "01_locatie_pret_vanzare.png",
                    "wait": ".o_form_view",
                    "highlight": ["div[name='store_pricelist_id']", "div[name='user_id']"],
                    "settle": 2000,
                },
                # 2. Recepția validată, cu delegatul și mijlocul de transport
                {
                    "url": (f"action={act_picking.id}&id={self.picking_nir.id}&model=stock.picking&view_type=form"),
                    "name": "02_receptie_delegat.png",
                    "wait": ".o_form_view",
                    # cele două câmpuri stau în tabul „Informații suplimentare", lângă responsabil
                    "click_tab": "Informații suplimentare",
                    "highlight": ["div[name='delegate_id']", "div[name='mean_transp']"],
                    "settle": 2500,
                },
                # 3. Meniul Tipăriți, cu cele șapte rapoarte
                {
                    "url": (f"action={act_picking.id}&id={self.picking_nir.id}&model=stock.picking&view_type=form"),
                    "name": "03_meniu_tiparire.png",
                    "wait": ".o_form_view",
                    # în Odoo 19 rapoartele stau în roata dințată din breadcrumb (web.CogMenu),
                    # iar cele șapte se grupează într-un submeniu „Tipăriți" care se desfășoară
                    # abia la al doilea click — de aici pasul suplimentar din `eval`
                    "click_btn": ".o_cp_action_menus button[data-hotkey='u']",
                    "wait_after": ".o-dropdown--menu",
                    "eval": (
                        "(() => {"
                        " const items = [...document.querySelectorAll('.o-dropdown--menu button')];"
                        " const t = items.find(e => /Tip[ăa]r/i.test(e.textContent));"
                        " if (t) { t.click(); }"
                        "})()"
                    ),
                    "eval_wait": 1500,
                    "settle": 2000,
                },
                # 4. NIR-ul standard
                self.report_shot(
                    "l10n_ro_stock_picking_report.action_report_reception",
                    self.picking_nir,
                    "04_nir.png",
                ),
                # 5. NIR fără taxe
                self.report_shot(
                    "l10n_ro_stock_picking_report.action_report_reception_no_tax",
                    self.picking_nir,
                    "05_nir_fara_taxe.png",
                ),
                # 6. NIR cu preț de vânzare
                self.report_shot(
                    "l10n_ro_stock_picking_report.action_report_reception_sale_price",
                    self.picking_nir,
                    "06_nir_pret_vanzare.png",
                ),
                # 7. Recepția în cutii de 13 kg, pe formular
                {
                    "url": (f"action={act_picking.id}&id={self.picking_cutii.id}&model=stock.picking&view_type=form"),
                    "name": "07_receptie_cutii.png",
                    "wait": ".o_form_view",
                    "settle": 2500,
                },
                # 8. NIR-ul pe recepția în unități de ambalare — cantitate, preț și valoare pe cutie
                self.report_shot(
                    "l10n_ro_stock_picking_report.action_report_reception",
                    self.picking_cutii,
                    "08_nir_unitate_ambalare.png",
                ),
                # 9. Avizul de însoțire a mărfii
                self.report_shot(
                    "l10n_ro_stock_picking_report.action_report_delivery_price",
                    self.picking_aviz,
                    "09_aviz_insotire.png",
                ),
                # 10. Bonul de consum
                self.report_shot(
                    "l10n_ro_stock_picking_report.action_report_consume_voucher",
                    self.picking_consum,
                    "10_bon_consum.png",
                ),
                # 11. Nota de transfer intern
                self.report_shot(
                    "l10n_ro_stock_picking_report.action_report_internal_transfer",
                    self.picking_transfer,
                    "11_transfer_intern.png",
                ),
                # 12. Dialogul raportului cumulativ
                {
                    # acțiunea e `target="new"`, deci se deschide ca dialog; îi dăm și `id`,
                    # ca dialogul să apară completat, nu gol
                    "url": (
                        f"action={action_cumulativ.id}&id={self.cumulative.id}"
                        "&model=stock.picking.cumulative&view_type=form"
                    ),
                    "name": "12_wizard_cumulativ.png",
                    "wait": ".modal-content",
                    # fără fundalul gri și lipit de marginea de sus, ca autotrim-ul să
                    # poată tăia zona moartă din jurul dialogului
                    "eval": (
                        "(() => {"
                        " document.querySelectorAll('.modal-backdrop, .o_main_navbar')"
                        "   .forEach(e => e.remove());"
                        " document.querySelectorAll('.modal-dialog').forEach(d => {"
                        "   d.classList.remove('modal-dialog-centered');"
                        "   d.style.margin = '8px auto';"
                        " });"
                        " if (document.activeElement) { document.activeElement.blur(); }"
                        " const m = document.querySelector('.modal');"
                        " if (m) { m.style.background = 'transparent'; }"
                        "})()"
                    ),
                    "settle": 2500,
                },
                # 13. Recepția cumulativă cu preț de vânzare
                self.report_shot(
                    "l10n_ro_stock_picking_report.action_report_c_recep_sale_price",
                    self.cumulative,
                    "13_receptie_cumulativa.png",
                ),
            ],
            hide_systray=True,
        )
