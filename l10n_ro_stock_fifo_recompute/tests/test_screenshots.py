# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi de ecran pentru fișa „Recalculare evaluare FIFO", generate în timpul
# testelor, în limba RO, pe planul de conturi RO.
#
# Seed (compensarea stocului negativ dezactivată pe companie):
#   - Marfă A (preț standard 80): livrare 3 buc pe stoc negativ (240), apoi recepție
#     5 buc @ 100 -> livrarea trebuie să fie 300 (CA1, Dr 607 / Cr 371);
#   - Marfă B (preț standard 80), în decembrie 2025, exercițiu închis: transfer 4 buc
#     din gestiunea goală Depozit 2 în Depozit 3 (320), recepție 4 buc @ 100 în
#     Depozit 2, livrare 4 buc din Depozit 3 (320) -> transferul și livrarea trebuie
#     să fie 400 (CA2: 371 destinație / 371 sursă; CA5: livrarea pe 1174);
#   - Marfă C (preț standard 120): livrare 3 buc pe stoc negativ (360), recepție
#     5 buc @ 100 -> livrarea trebuie să fie 300, diferență negativă, storno (CA4).
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> \
#       -i l10n_ro_stock_fifo_recompute,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import unittest
from datetime import date, datetime

from odoo import Command
from odoo.tests import tagged
from odoo.tools import SQL

from odoo.addons.l10n_ro_stock_account.tests.common import TestROStockCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import (
        ScreenshotCase,
    )
except ImportError:
    ScreenshotCase = None


# Formularul pe toată lățimea, ca toate coloanele diferențelor să încapă
WIDE_FORM = (
    "(() => { const st = document.createElement('style');"
    " st.textContent = '.o_form_view .o_form_sheet_bg, .o_form_view .o_form_renderer"
    " { max-width: none !important; }';"
    " document.head.appendChild(st); })()"
)


@tagged("-at_install", "post_install", "fise_screenshots")
class TestFifoRecomputeScreenshots(TestROStockCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_fifo_recompute"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        company = cls.prepare_ro_company(name="Demo Stocuri SRL")
        cls.env.ref("base.user_admin").write({"company_ids": [(4, company.id)], "company_id": company.id})
        cls.env = cls.env(context=dict(cls.env.context, lang="ro_RO"))
        company.fifo_location_negative_compensation = False
        for location, code in (
            (cls.location, "D1"),
            (cls.location1, "D2"),
            (cls.location2, "D3"),
        ):
            location.warehouse_id.write({"name": f"Depozit {code}", "code": code})
            location.name = "Stoc"
        cls.env.ref("stock.stock_location_customers").name = "Clienți"
        cls.stock_journal.write({"name": "Note de stoc", "code": "STOC"})
        cls.account_valuation_wh3 = company.account_stock_valuation_id.copy(
            {"code": "371003", "name": "Mărfuri Depozit D3"}
        )
        cls.location1.l10n_ro_property_stock_valuation_account_id.name = "Mărfuri Depozit D2"
        cls.location2.l10n_ro_property_stock_valuation_account_id = cls.account_valuation_wh3
        cls.account_closed = cls.env["l10n.ro.fifo.recompute"]._default_account_closed()
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.supplier_1.name = "Furnizor Exemplu SRL"
        cls.customer_1.name = "Client Exemplu SRL"
        cls.marfa_a = cls._new_product("Marfă A", 80.0)
        cls.marfa_b = cls._new_product("Marfă B", 80.0)
        cls.marfa_c = cls._new_product("Marfă C", 120.0)

    @classmethod
    def _new_product(cls, name, standard_price):
        return cls.env["product.product"].create(
            {
                "name": name,
                "is_storable": True,
                "categ_id": cls.product_fifo.categ_id.id,
                "invoice_policy": "delivery",
                "purchase_method": "receive",
                "standard_price": standard_price,
            }
        )

    # ------------------------------------------------------------------
    # Seed
    # ------------------------------------------------------------------
    def _receive(self, product, qty, price, index, location=None):
        values = {
            "currency_id": self.ron,
            "partner_id": self.supplier_1,
            "product_id": product,
            "qty": qty,
            "stock_qty": qty,
            "inv_qty": qty,
            "price": price,
            "inv_price": price,
            "index": index,
        }
        if location:
            values["location"] = location
        purchase = self.create_purchase(values)
        return purchase, purchase.picking_ids.move_ids.filtered(lambda m: m.state == "done")

    def _deliver(self, product, qty, index):
        sale = self.create_sale_order(
            {
                "currency_id": self.ron,
                "partner_id": self.customer_1,
                "product_id": product,
                "qty": qty,
                "stock_qty": qty,
                "inv_qty": qty,
                "price": 150,
                "inv_price": 150,
                "advance": 0,
                "discount": 0,
                "index": index,
            }
        )
        return sale.picking_ids.move_ids.filtered(lambda m: m.product_id == product and m.state == "done")

    def _picking(self, picking_type, location_src, location_dest, product, qty):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": self.customer_1.id,
                "location_id": location_src.id,
                "location_dest_id": location_dest.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": location_src.id,
                            "location_dest_id": location_dest.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids._set_quantity_done(qty)
        picking.move_ids.picked = True
        picking._action_done()
        return picking.move_ids

    def _seed(self):
        # CA1: livrare pe stoc negativ, evaluată la prețul standard, apoi recepție
        self.out_a = self._deliver(self.marfa_a, 3, "sa")
        self._receive(self.marfa_a, 5, 100, "pa")
        # CA2 + CA5: transfer între gestiuni cu conturi diferite, în exercițiul închis
        wh2 = self.location1.warehouse_id
        wh3 = self.location2.warehouse_id
        self.transfer_b = self._picking(wh2.int_type_id, self.location1, self.location2, self.marfa_b, 4)
        purchase_b, receipt_b = self._receive(self.marfa_b, 4, 100, "pb", location=self.location1)
        self.out_b = self._picking(wh3.out_type_id, self.location2, self.customers, self.marfa_b, 4)
        self.transfer_b.date = datetime(2025, 12, 10, 10, 0)
        receipt_b.date = datetime(2025, 12, 12, 10, 0)
        self.out_b.date = datetime(2025, 12, 15, 10, 0)
        self.env.cr.execute(
            SQL(
                "UPDATE account_move SET invoice_date = %s WHERE id IN %s",
                date(2025, 12, 12),
                tuple(purchase_b.invoice_ids.ids),
            )
        )
        self.env.invalidate_all()
        # CA4: ieșire supraevaluată, corectată în roșu
        self.out_c = self._deliver(self.marfa_c, 3, "sc")
        self._receive(self.marfa_c, 5, 100, "pc")

    # ------------------------------------------------------------------
    # Capturi
    # ------------------------------------------------------------------
    def test_capture_fise(self):
        action = self.env.ref("l10n_ro_stock_fifo_recompute.action_l10n_ro_fifo_recompute")
        menu = self.env.ref("l10n_ro_stock_fifo_recompute.menu_l10n_ro_fifo_recompute")
        line_action = self.env.ref("l10n_ro_stock_fifo_recompute.action_l10n_ro_fifo_recompute_line")
        opts = {"viewport": (1920, 1000), "hide_systray": True}
        model = "l10n.ro.fifo.recompute"

        # 1. Meniul, încă fără rulări
        self.capture_screenshots(
            [
                {
                    "url": f"action={action.id}&menu_id={menu.id}",
                    "name": "01_lista_recalculari.png",
                    "wait": ".o_action_manager .o_view_controller",
                    "highlight": [".o_list_button_add"],
                    "settle": 2000,
                }
            ],
            **opts,
        )

        self._seed()
        recompute = self.env[model].create(
            {
                "product_ids": [Command.set((self.marfa_a | self.marfa_b | self.marfa_c).ids)],
                "closed_year_date": date(2025, 12, 31),
                "account_closed_id": self.account_closed.id,
            }
        )
        form = f"id={recompute.id}&action={action.id}&menu_id={menu.id}&model={model}&view_type=form"

        # 2. Rularea nouă, completată, înainte de Calculează
        self.capture_screenshots(
            [
                {
                    "url": form,
                    "name": "02_rulare_noua.png",
                    "eval": WIDE_FORM,
                    "wait": ".o_form_view",
                    "highlight": [
                        "div[name='product_ids']",
                        "div[name='date']",
                        "div[name='closed_year_date']",
                        "div[name='account_closed_id']",
                        "button[name='action_compute']",
                    ],
                    "settle": 2000,
                }
            ],
            **opts,
        )

        recompute.action_compute()
        self.assertEqual(len(recompute.line_ids), 4)

        # 3-6. Diferențe, Control conturi, lista filtrabilă, confirmarea aplicării
        self.capture_screenshots(
            [
                {
                    "url": form,
                    "name": "03_diferente.png",
                    "eval": WIDE_FORM,
                    "wait": ".o_form_view",
                    "full": True,
                    "highlight": ["div[name='total_delta']"],
                    "settle": 2500,
                },
                {
                    "url": form,
                    "name": "04_control_conturi.png",
                    "eval": WIDE_FORM,
                    "wait": ".o_form_view",
                    "click_tab": "Control conturi",
                    "full": True,
                    "settle": 2500,
                },
                {
                    "url": form,
                    "name": "05_lista_diferente.png",
                    "wait": ".o_form_view",
                    "click_btn": f"button[name='{line_action.id}']",
                    "wait_after": ".o_list_view",
                    "full": True,
                    "settle": 2500,
                },
                {
                    "url": form,
                    "name": "06_confirmare_aplicare.png",
                    "eval": WIDE_FORM,
                    "wait": ".o_form_view",
                    "click_btn": "button[name='action_apply']",
                    "wait_after": ".modal-content",
                    "settle": 2000,
                },
            ],
            **opts,
        )

        recompute.action_apply()
        self.assertEqual(recompute.state, "applied")

        # 7-8. Rularea aplicată și nota de corecție
        self.capture_screenshots(
            [
                {
                    "url": form,
                    "name": "07_rulare_aplicata.png",
                    "eval": WIDE_FORM,
                    "wait": ".o_form_view",
                    "highlight": ["button[name='action_view_account_move']"],
                    "settle": 2000,
                },
                self.account_move_shot(recompute.account_move_id, "08_nota_corectie.png"),
            ],
            **opts,
        )
