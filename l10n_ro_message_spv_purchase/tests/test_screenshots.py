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
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> \
#       -i l10n_ro_message_spv_purchase,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import unittest

from odoo import fields
from odoo.tests import tagged

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


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
        cls.env.flush_all()

    def test_capture_fise(self):
        self.assertEqual(self.message.currency_id.name, "RON", "Capturile trebuie să iasă în RON, nu în USD")
        self.assertEqual(
            self.message.message_type,
            "in_invoice",
            "Butoanele modulului apar doar pe mesajele de achiziție — seed-ul trebuie să fie in_invoice",
        )

        self.capture_screenshots(
            [
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
            ],
            viewport=(1700, 1000),
        )
