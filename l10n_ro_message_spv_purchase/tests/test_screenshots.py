# © 2026 Deltatech
# Dorin Hongu <dhongu(@)gmail(.)com>
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa consultant a modulului — generate în timpul testelor, în RO.
#
# Modulul nu avea nicio captură. Aceasta este prima: formularul mesajului SPV cu cele două
# butoane adăugate de modul (Găsește Comanda / Creează Comanda) și câmpurile Purchase
# Reference / Purchase Order pe care operatorul le verifică înainte de a apăsa.
#
# Cu deltatech_purchase_ubl instalat, se adaugă cele două rezultate posibile ale butonului
# „Creează Comanda" (19.0.0.0.10): importul direct al unei facturi curate, cu notificarea, și
# previzualizarea deschisă pentru o factură cu o linie neidentificată.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> \
#       -i l10n_ro_message_spv_purchase,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import io
import unittest
import zipfile

from odoo import fields
from odoo.tests import tagged

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None

try:
    from odoo.addons.deltatech_purchase_ubl.tests.test_process_attachments import _xml_invoice
except ImportError:
    _xml_invoice = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestMessageSpvPurchaseScreenshots(ScreenshotCase or object):
    screenshots_module = "l10n_ro_message_spv_purchase"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        # Compania demo a localizării RO („RO Company", RON, plan de conturi RO) — compania
        # principală e în USD și moneda nu mai poate fi schimbată o dată ce are note contabile.
        company = cls.prepare_demo_company()
        cls.env = cls.env(context=dict(cls.env.context, allowed_company_ids=[company.id]))
        # Compania demo RO nu are depozit (spre deosebire de compania principală), iar fără
        # el `purchase.order.picking_type_id` rămâne null și `create` cade pe constrângerea
        # NOT NULL din bază.
        if not cls.env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1):
            cls.env["stock.warehouse"].create({"name": "Depozit Central", "code": "DPC", "company_id": company.id})

        env = cls.env
        cls.vendor = env["res.partner"].create(
            {
                "name": "Furnizor Materiale SRL",
                "is_company": True,
                "vat": "RO12345674",
                "supplier_rank": 1,
                "country_id": env.ref("base.ro").id,
            }
        )
        # Comanda pe care butonul „Găsește Comanda" o va identifica după referință —
        # există ca ecranul să nu sugereze un caz fără potrivire.
        cls.purchase = env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "company_id": company.id,
                "partner_ref": "CMD-2026-0418",
            }
        )
        # Mesajul SPV: tip `in_invoice`, altfel butoanele modulului sunt invizibile
        # (`invisible="message_type not in ('in_invoice', 'in_receipt')"`).
        cls.message = env["l10n.ro.message.spv"].create(
            {
                "name": "5138472916",
                "message_type": "in_invoice",
                "cif": "12345674",
                "ref": "FMS-2026-00418",
                "purchase_ref": "CMD-2026-0418",
                "partner_id": cls.vendor.id,
                "company_id": company.id,
                "date": fields.Datetime.now(),
                "invoice_date": fields.Date.today(),
                "amount": 843.60,
                "details": "Factura FMS-2026-00418 emisă de Furnizor Materiale SRL",
                "request_id": "4471028365",
                "state": "draft",
            }
        )
        cls.message_clean = cls.message_review = False
        if _xml_invoice and "purchase.ubl.import.wizard" in env:
            product = env["product.product"].create({"name": "Cot PVC 110 mm", "type": "consu"})
            env["product.supplierinfo"].create(
                {
                    "partner_id": cls.vendor.id,
                    "product_tmpl_id": product.product_tmpl_id.id,
                    "product_id": product.id,
                    "product_code": "FM-COT-110",
                    "price": 12.50,
                }
            )
            known = {
                "code": "FM-COT-110",
                "name": "Cot PVC 110 mm",
                "qty": "40",
                "price": "12.50",
                "line_total": "500.00",
            }
            unknown = {
                "code": "FM-RED-063",
                "name": "Reductie PVC 110/63 mm",
                "qty": "8",
                "price": "9.20",
                "line_total": "73.60",
            }
            cls.message_clean = cls._message_with_xml(company, "5138472917", "FMS-2026-00420", "CMD-2026-0420", [known])
            cls.message_review = cls._message_with_xml(
                company, "5138472918", "FMS-2026-00421", "CMD-2026-0421", [known, unknown]
            )
        cls.env.flush_all()

    @classmethod
    def _message_with_xml(cls, company, name, ref, purchase_ref, lines):
        """Mesaj SPV cu ZIP-ul ANAF descărcat, cum îl aduce cronul: XML-ul se ia din ZIP."""
        xml = _xml_invoice(
            invoice_id=ref,
            order_ref=purchase_ref,
            supplier_vat="12345674",
            supplier_name="Furnizor Materiale SRL",
            lines=lines,
        )
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(f"{name}.xml", xml)
        message = cls.env["l10n.ro.message.spv"].create(
            {
                "name": name,
                "message_type": "in_invoice",
                "cif": "12345674",
                "ref": ref,
                "purchase_ref": purchase_ref,
                "partner_id": cls.vendor.id,
                "company_id": company.id,
                "date": fields.Datetime.now(),
                "invoice_date": fields.Date.today(),
                "state": "draft",
            }
        )
        message.attachment_id = cls.env["ir.attachment"].create(
            {"name": f"{name}.zip", "raw": buffer.getvalue(), "res_model": message._name, "res_id": message.id}
        )
        return message

    def test_capture_fise(self):
        self.assertEqual(self.message.currency_id.name, "RON", "Capturile trebuie să iasă în RON, nu în USD")
        self.assertEqual(
            self.message.message_type,
            "in_invoice",
            "Butoanele modulului apar doar pe mesajele de achiziție — seed-ul trebuie să fie in_invoice",
        )

        shots = [
            {
                "url": f"id={self.message.id}&model=l10n.ro.message.spv&view_type=form",
                "name": "01_mesaj_spv_butoane.png",
                "wait": ".o_form_view",
                # ① butonul de căutare, ② butonul de creare, ③ câmpurile adăugate de modul
                "highlight": [
                    "button[name='action_find_purchase']",
                    "button[name='action_create_purchase']",
                    "div[name='purchase_ref']",
                ],
                "settle": 2500,
                "full": True,
            },
        ]
        if self.message_clean:
            shots += [
                # Factură curată: importul se face direct; ① notificarea, peste comanda deschisă.
                {
                    "url": f"id={self.message_clean.id}&model=l10n.ro.message.spv&view_type=form",
                    "name": "02_notificare_import_direct.png",
                    "wait": ".o_form_view",
                    "click_btn": "button[name='action_create_purchase']",
                    # notificarea, apoi comanda deschisă de acțiunea ei `next`
                    "wait_after": ".o_notification",
                    "eval": "(async () => {await new Promise(r => setTimeout(r, 1500));})()",
                    "eval_wait": 300,
                    "highlight": [".o_notification", ".o_breadcrumb"],
                    "settle": 300,
                },
                # Factură cu o linie neidentificată: previzualizarea, cu ① linia pe „Ignoră".
                {
                    "url": f"id={self.message_review.id}&model=l10n.ro.message.spv&view_type=form",
                    "name": "03_preview_decizie_linii.png",
                    "wait": ".o_form_view",
                    "click_btn": "button[name='action_create_purchase']",
                    "wait_after": ".modal .o_list_view",
                    "highlight": [".modal tr.o_data_row:has-text('Reductie PVC') td[name='line_action']"],
                    "settle": 2000,
                },
            ]
        self.capture_screenshots(shots, viewport=(1700, 1000))
