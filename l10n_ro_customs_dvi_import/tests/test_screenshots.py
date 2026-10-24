# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi de ecran pentru fișa „Importul DVI din PDF-ul SNI” — generate în timpul testelor, în
# limba RO, pe planul de conturi RO.
#
# PDF-urile reale ale declarațiilor nu intră în repo (au datele clienților). Citirea PDF-ului e
# înlocuită cu liniile anonimizate din tests/data: fișierul încărcat în browser conține doar numele
# fixture-ului, iar `extract_lines` îl întoarce pe acela. Restul fluxului (wizardul, verificările,
# DVI-ul, nota) rulează neschimbat.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_customs_dvi_import,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import base64
import json
import unittest
from unittest.mock import patch

from odoo import Command
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from .common import IMPORTER_VAT, load_lines

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None

EXTRACT_LINES = "odoo.addons.l10n_ro_customs_dvi_import.tools.sni_dvi.extract_lines"
FIXTURE_TAG = b"fixture:"


def _fixture_content(name):
    return b"%PDF-1.4 " + FIXTURE_TAG + name.encode()


def _fake_extract_lines(content):
    return load_lines(content.split(FIXTURE_TAG)[1].decode().strip())


def _upload_js(fixture, filename):
    """Încarcă în câmpul „PDF DVI (SNI)” al wizardului un fișier cu numele fixture-ului."""
    content = json.dumps(_fixture_content(fixture).decode())
    return (
        "const input = document.querySelector(\".modal-content div[name='dvi_file'] input[type=file]\");"
        f"const file = new File([{content}], {json.dumps(filename)}, {{type: 'application/pdf'}});"
        "const dt = new DataTransfer(); dt.items.add(file); input.files = dt.files;"
        "input.dispatchEvent(new Event('change', {bubbles: true}));"
    )


def _pad_highlighted(*names):
    """Insigna numerotată stă în colțul câmpului: fără spațiu, acoperă începutul valorii.

    Se aplică după completarea wizardului: câmpurile care apar abia atunci (garanția la 4200) nu
    există încă în pagină la încărcarea fișierului.
    """
    selector = ", ".join(f".modal-content div[name='{name}']" for name in names)
    return (
        f"setTimeout(() => document.querySelectorAll({json.dumps(selector)}).forEach(e => {{"
        " e.style.paddingLeft = '18px';"
        " e.querySelectorAll('input').forEach(i => { i.style.paddingLeft = '18px'; }); }), 1500);"
    )


@tagged("-at_install", "post_install", "fise_screenshots")
class TestCustomsDviImportScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_customs_dvi_import"

    QTY = 1000.0

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Demo Import SRL")
        env = cls.env
        company = env.company
        # importatorul din declarațiile anonimizate
        company.vat = IMPORTER_VAT
        env.ref("base.user_admin").write({"company_ids": [(4, company.id)], "company_id": company.id})
        # autorul mesajului din istoricul DVI-ului, vizibil în captura 04
        env.user.name = "Contabil Importuri"
        # Produsul „Taxă vamală” e unic pe bază și poate fi creat într-o sesiune în engleză: în
        # capturi, linia de cost ar apărea „Custom Duty”.
        duty_product = env["account.invoice.dvi"].get_custom_duty_product()
        if duty_product:
            duty_product.with_context(lang="ro_RO").name = "Taxă vamală"

        warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        warehouse.name = "Terminal Vamal"
        categ = env["product.category"].create(
            {"name": "Fructe import", "property_cost_method": "fifo", "property_valuation": "real_time"}
        )
        cls.product = env["product.product"].create(
            {"name": "Mere proaspete", "is_storable": True, "categ_id": categ.id, "standard_price": 1}
        )
        cls.partner = env["res.partner"].create({"name": "Exportator Fructe SRL", "country_id": env.ref("base.md").id})

        # Facturile au ca referință numărul facturii din declarație (documentul N380).
        cls.bill_4000 = cls._seed_posted_bill(warehouse, "EXP/2026/00001", 47.70)
        cls.bill_4200 = cls._seed_posted_bill(warehouse, "11EX", 67.94)
        cls.bill_done = cls._seed_posted_bill(warehouse, "CI-20260101-ABC-001", 4.97)
        cls.bill_duplicate = cls._seed_posted_bill(warehouse, "EXP/2026/00005", 58.71)

        # DVI-ul complet, pentru capturile cu declarația atașată și cu nota contabilă: declarația
        # cu taxă vamală (A00 = 144) și TVA 21%, ca nota să arate și costul stocului
        with patch(EXTRACT_LINES, side_effect=_fake_extract_lines):
            wizard_form = Form(env["account.invoice.dvi"].with_context(active_id=cls.bill_done.id, lang="ro_RO"))
            wizard_form.dvi_file = base64.b64encode(_fixture_content("dvi_4000_customs_duty"))
            wizard = wizard_form.save()
            wizard.dvi_filename = "26ROXX0000000005R5.pdf"
            wizard.with_context(active_id=cls.bill_done.id, lang="ro_RO").do_create_dvi()
        cls.landed_cost = cls.bill_done.dvi_id
        cls.landed_cost.compute_landed_cost()
        cls.landed_cost.with_context(lang="ro_RO").button_validate()

    @classmethod
    def _seed_posted_bill(cls, warehouse, ref, price):
        po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": warehouse.in_type_id.id,
                "order_line": [
                    Command.create({"product_id": cls.product.id, "product_qty": cls.QTY, "price_unit": price})
                ],
            }
        )
        po.button_confirm()
        receipt = po.picking_ids[0]
        receipt.action_assign()
        for move_line in receipt.move_line_ids:
            move_line.quantity = cls.QTY
        # demo_mode: sare peste validarea de curier din l10n_ro_edi_stock (eTransport)
        receipt.with_context(demo_mode=True).button_validate()
        po.action_create_invoice()
        bill = po.invoice_ids[0]
        bill.write({"ref": ref, "invoice_date": bill.date})
        bill.action_post()
        return bill

    def _wizard_shot(self, bill, name, **extra):
        shot = {
            "url": f"id={bill.id}&model=account.move&view_type=form",
            "name": name,
            "wait": ".o_form_view",
            "click_btn": "button[name='button_dvi']",
            "wait_after": ".modal-content",
            "settle": 2500,
        }
        shot.update(extra)
        return shot

    def test_capture_fise(self):
        with patch(EXTRACT_LINES, side_effect=_fake_extract_lines):
            self.capture_screenshots(
                viewport=(1920, 1350),
                shots=[
                    # 1. Wizardul deschis de pe factură, cu câmpul nou pentru PDF
                    self._wizard_shot(
                        self.bill_4000,
                        "01_wizard_incarcare_pdf.png",
                        highlight=[".modal-content div[name='dvi_file']"],
                    ),
                    # 2. Regim 4000: valorile citite, caseta de control și avertismentul despre taxă
                    self._wizard_shot(
                        self.bill_4000,
                        "02_wizard_completat_din_pdf.png",
                        eval=_upload_js("dvi_4000_two_items", "26ROXX0000000001R1.pdf")
                        + _pad_highlighted("dvi_number", "tax_id", "tax_base", "tax_value"),
                        eval_wait=2500,
                        highlight=[
                            ".modal-content div[name='dvi_number']",
                            ".modal-content div[name='tax_id']",
                            ".modal-content div[name='tax_base']",
                            ".modal-content div[name='tax_value']",
                        ],
                    ),
                    # 3. Regim 4200: B00 devine garanție, fără TVA de import
                    self._wizard_shot(
                        self.bill_4200,
                        "03_wizard_4200_garantie.png",
                        eval=_upload_js("dvi_4200_two_items", "26ROXX0000000004R4.pdf")
                        + _pad_highlighted("customs_regime", "vat_guarantee_amount"),
                        eval_wait=2500,
                        highlight=[
                            ".modal-content div[name='customs_regime']",
                            ".modal-content div[name='vat_guarantee_amount']",
                        ],
                    ),
                    # 4. DVI-ul creat, cu PDF-ul atașat și rezumatul în istoric
                    {
                        "url": f"id={self.landed_cost.id}&model=stock.landed.cost&view_type=form",
                        "name": "04_dvi_pdf_atasat.png",
                        "wait": ".o_form_view",
                        "hide_chatter": False,
                        "highlight": ["div[name='dvi_number']", ".o-mail-Message:has-text('SNI')"],
                        "settle": 2500,
                        "full": True,
                    },
                    # 5. Nota contabilă, cu MRN-ul ca referință
                    self.account_move_shot(self.landed_cost.account_move_id, "05_nota_contabila.png"),
                    # 6. A doua încărcare a aceleiași declarații e refuzată
                    self._wizard_shot(
                        self.bill_duplicate,
                        "06_eroare_declaratie_inregistrata.png",
                        eval=_upload_js("dvi_4000_customs_duty", "26ROXX0000000005R5.pdf"),
                        eval_wait=3000,
                    ),
                ],
            )
