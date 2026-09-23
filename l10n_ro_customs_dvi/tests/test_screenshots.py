# © 2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Declarația Vamală de Import (DVI) ca cost de aterizare" —
# generate în timpul testelor, în limba RO, pe planul de conturi RO.
#
# Seedează un import non-UE cu cifre verificabile, alese ca să arate exact capcana din fișă:
# factura furnizorului e de 60.000 lei, dar baza de impozitare din declarație e 70.000 lei,
# pentru că valoarea în vamă include transportul extern (9.000) şi taxa vamală (1.000).
# Odoo propune netul facturii; operatorul trebuie să transcrie baza din DVI.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_customs_dvi,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import unittest

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestCustomsDviScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_customs_dvi"

    # Cifrele fișei — ținute aici, într-un singur loc, ca să rămână coerente cu textul.
    QTY = 1000.0
    PRICE = 60.0  # 1.000 kg x 60,00 = 60.000,00 lei pe factura furnizorului
    CUSTOM_DUTY = 1000.0  # poziția A00
    # Baza B00 din declarație: valoarea în vamă (marfă 60.000 + transport extern 9.000)
    # + taxa vamală 1.000. NU coincide cu netul facturii — ăsta e tot rostul capturii.
    TAX_BASE = 70000.0
    VAT_RATE = 11.0  # mere = aliment de bază, cotă redusă (art. 291 alin. (2))

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Demo Import SRL")
        env = cls.env
        company = env.company
        env.ref("base.user_admin").write({"company_ids": [(4, company.id)], "company_id": company.id})

        # Listele de prețuri rămân pe moneda bazei de test, așa că pe fișa produsului
        # „Preț vânzare" ieșea în dolari lângă „Cost" în lei. În capturile unei fișe RO,
        # două monede pe același ecran arată a neglijență.
        ron = env.ref("base.RON")
        pricelists = env["product.pricelist"].search(["|", ("company_id", "=", company.id), ("company_id", "=", False)])
        if pricelists:
            pricelists.write({"currency_id": ron.id})

        cls.warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        # Denumiri RO, ca în capturi să nu apară string-uri tehnice de test
        cls.warehouse.name = "Terminal Vamal"
        cls.warehouse.in_type_id.name = "Recepții"
        cls.warehouse.out_type_id.name = "Livrări"

        acc_371 = env["account.account"].search(
            [("code", "=like", "371%"), ("company_ids", "in", [company.id])], order="code", limit=1
        )
        acc_607 = env["account.account"].search(
            [("code", "=like", "607%"), ("company_ids", "in", [company.id])], order="code", limit=1
        )
        if acc_371 and acc_607:
            acc_371.account_stock_variation_id = acc_607.id

        # Evaluare perpetuă (la facturare) + cost mediu: fără ele, DVI-ul nu postează (Pasul 1 din fișă)
        cls.categ = env["product.category"].create(
            {
                "name": "Mărfuri import (AVCO)",
                "property_cost_method": "average",
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": acc_371.id if acc_371 else False,
            }
        )
        cls.product = env["product.product"].create(
            {
                "name": "Mere",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.categ.id,
                "standard_price": cls.PRICE,
            }
        )
        cls.partner = env["res.partner"].create({"name": "Pro Inedit SRL", "country_id": env.ref("base.md").id})
        cls.broker = env["res.partner"].create({"name": "Comisionar Vamal SRL", "country_id": env.ref("base.ro").id})

        # Cota de TVA aplicată de vamă. Merele sunt aliment de bază -> cotă redusă,
        # nu taxa de achiziție implicită a companiei.
        cls.tax_import = env["account.tax"].search(
            [
                ("company_id", "=", company.id),
                ("type_tax_use", "=", "purchase"),
                ("amount", "=", cls.VAT_RATE),
                ("amount_type", "=", "percent"),
            ],
            limit=1,
        )
        if not cls.tax_import:
            cls.tax_import = env["account.tax"].search(
                [("company_id", "=", company.id), ("type_tax_use", "=", "purchase")], limit=1
            )

        cls.journal = env["account.journal"].search(
            [("type", "=", "general"), ("company_id", "=", company.id)], limit=1
        )

        # --- Factura A: rămâne fără DVI, ca wizardul să poată fi pozat în starea lui reală.
        # Folosește un produs SEPARAT, ca fluxul principal să rămână pe o singură recepție și
        # costul mediu al mărfii să iasă exact (60,00 + 1.000/1.000 = 61,00). ---
        cls.product_wizard = env["product.product"].create(
            {
                "name": "Pere",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.categ.id,
                "standard_price": cls.PRICE,
            }
        )
        cls.po_a = cls._seed_import_order(env, product=cls.product_wizard)
        cls.bill_a = cls._seed_posted_bill(cls.po_a)

        # --- Factura B: DVI creat și validat, pentru notă, cost de aterizare și cost produs ---
        cls.po_b = cls._seed_import_order(env)
        cls.receipt_b = cls.po_b.picking_ids[0]
        cls.bill_b = cls._seed_posted_bill(cls.po_b)

        wizard = (
            env["account.invoice.dvi"]
            .with_context(active_id=cls.bill_b.id, lang="ro_RO")
            .create(
                {
                    "date": cls.bill_b.invoice_date,
                    "dvi_number": "26ROIS0600123456",
                    "custom_duty": cls.CUSTOM_DUTY,
                    "tax_id": cls.tax_import.id,
                    "tax_base": cls.TAX_BASE,
                    "tax_value": cls.TAX_BASE * cls.VAT_RATE / 100.0,
                }
            )
        )
        wizard.with_context(active_id=cls.bill_b.id, lang="ro_RO").do_create_dvi()
        cls.landed_cost = cls.bill_b.dvi_id
        cls.landed_cost.compute_landed_cost()
        cls.landed_cost.with_context(lang="ro_RO").button_validate()
        cls.vat_move = cls.landed_cost.account_move_id

        # --- Factura brokerului: produs de serviciu marcat drept cost de aterizare ---
        # Contul produsului brokerului: 473 „Decontări din operațiuni în curs de clarificare",
        # cont de tranzit neutru, conform recomandării din fișă — onorariul se capitalizează,
        # deci trece prin 473 și se soldează la validarea costului adițional. Fără cont propriu,
        # produsul ar cădea pe contul categoriei (607) și captura ar contrazice textul.
        acc_transit = env["account.account"].search(
            [("code", "=like", "473%"), ("company_ids", "in", [company.id])], order="code", limit=1
        ) or env["account.account"].search(
            [("code", "=like", "622%"), ("company_ids", "in", [company.id])], order="code", limit=1
        )
        cls.broker_product = env["product.product"].create(
            {
                "name": "Onorariu comisionar vamal",
                "type": "service",
                "landed_cost_ok": True,
                "split_method_landed_cost": "by_current_cost_price",
                "property_account_expense_id": acc_transit.id if acc_transit else False,
            }
        )
        cls.broker_bill = env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": cls.broker.id,
                "invoice_date": cls.bill_b.invoice_date,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.broker_product.id,
                            "name": "Onorariu comisionar vamal DVI 26ROIS0600123456",
                            "quantity": 1.0,
                            "price_unit": 450.0,
                            # onchange-ul nu rulează la create prin ORM; îl setăm explicit,
                            # altfel butonul „Creează costuri de aterizare" nu apare
                            "is_landed_costs_line": True,
                        }
                    )
                ],
            }
        )
        cls.broker_bill.action_post()

    @classmethod
    def _seed_import_order(cls, env, product=None):
        """Comandă de achiziție confirmată + recepție validată la terminalul vamal."""
        product = product or cls.product
        po = env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_qty": cls.QTY,
                            "price_unit": cls.PRICE,
                        }
                    )
                ],
            }
        )
        po.button_confirm()
        receipt = po.picking_ids[0]
        receipt.action_assign()
        for ml in receipt.move_line_ids:
            ml.quantity = cls.QTY
        # demo_mode: sare peste validarea de curier din l10n_ro_edi_stock (eTransport)
        receipt.with_context(demo_mode=True).button_validate()
        return po

    @classmethod
    def _seed_posted_bill(cls, po):
        po.action_create_invoice()
        bill = po.invoice_ids[0]
        bill.invoice_date = bill.date
        bill.action_post()
        return bill

    def test_capture_fise(self):
        action_dvi_list = self.env.ref("l10n_ro_customs_dvi.action_stock_landed_cost_dvi")
        self.capture_screenshots(
            [
                # 1. Categoria de produse — valorizare automată + CMP (capcana tăcută)
                {
                    "url": f"id={self.categ.id}&model=product.category&view_type=form",
                    "name": "01_config_categorie.png",
                    "wait": ".o_form_view",
                    "highlight": [
                        "div[name='property_cost_method']",
                        "div[name='property_valuation']",
                    ],
                    "settle": 2000,
                    "full": True,
                },
                # 2. Comanda de achiziție către furnizorul extern
                {
                    "url": f"id={self.po_b.id}&model=purchase.order&view_type=form",
                    "name": "02_po_import.png",
                    "wait": ".o_form_view",
                    "settle": 2000,
                    "full": True,
                },
                # 3. Recepția la terminalul vamal — obligatorie, DVI-ul se atașează pe ea
                {
                    "url": f"id={self.receipt_b.id}&model=stock.picking&view_type=form",
                    "name": "03_receptie_terminal.png",
                    "wait": ".o_form_view",
                    "settle": 2000,
                    "full": True,
                },
                # 4. Factura furnizorului, postată, cu butonul DVI
                {
                    "url": f"id={self.bill_b.id}&model=account.move&view_type=form",
                    "name": "04_factura_furnizor_buton_dvi.png",
                    "wait": ".o_form_view",
                    "highlight": ["button[name='button_dvi']"],
                    "settle": 2500,
                    "full": True,
                },
                # 5. Wizardul DVI, așa cum îl vede operatorul: baza precompletată e netul
                #    facturii (60.000), nu baza din declarație (70.200)
                {
                    "url": f"id={self.bill_a.id}&model=account.move&view_type=form",
                    "name": "05_wizard_dvi.png",
                    "wait": ".o_form_view",
                    "click_btn": "button[name='button_dvi']",
                    "wait_after": ".modal-content",
                    "settle": 2500,
                },
                # 6. Costul de aterizare generat, cu câmpurile DVI
                {
                    "url": f"id={self.landed_cost.id}&model=stock.landed.cost&view_type=form",
                    "name": "06_landed_cost_dvi.png",
                    "wait": ".o_form_view",
                    "highlight": ["div[name='dvi_number']", "div[name='tax_base']"],
                    "settle": 2000,
                    "full": True,
                },
                # 7. Nota contabilă — referința este MRN-ul, nu secvența internă
                self.account_move_shot(self.vat_move, "07_nota_contabila_tva.png"),
                # 8. Costul produsului, majorat cu taxa vamală și comisionul
                {
                    "url": f"id={self.product.product_tmpl_id.id}&model=product.template&view_type=form",
                    "name": "08_cost_produs.png",
                    "wait": ".o_form_view",
                    "highlight": ["div[name='standard_price']"],
                    "settle": 2000,
                    "full": True,
                },
                # 9. Factura brokerului — butonul nativ e switch-ul de politică contabilă
                {
                    "url": f"id={self.broker_bill.id}&model=account.move&view_type=form",
                    "name": "09_factura_broker.png",
                    "wait": ".o_form_view",
                    "highlight": ["button[name='button_create_landed_costs']"],
                    "settle": 2500,
                    "full": True,
                },
                # 10. Lista dedicată DVI — Costuri vamale, grupată pe dată
                {
                    "url": f"action={action_dvi_list.id}&model=stock.landed.cost&view_type=list",
                    "name": "10_lista_dvi.png",
                    "wait": ".o_list_view",
                    # grupul pe lună vine pliat; `click_btn` se execută înainte ca rândurile
                    # să fie randate, așa că desfacem grupul din pagină, după randare
                    "eval": (
                        "const h = document.querySelector('.o_group_header .o_group_name')"
                        " || document.querySelector('.o_group_header'); if (h) h.click();"
                    ),
                    "settle": 2500,
                    "full": True,
                },
            ]
        )
