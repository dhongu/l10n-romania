# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Factura, chitanța și dispoziția de casă" — generate în RO.
#
# Seedează: o factură de client postată cu delegat și mijloc de transport, o plată în numerar
# (dispoziție de plată, cod 14-4-4) și o încasare în numerar (chitanță / dispoziție de încasare,
# cod 14-4-1), plus randările tipăribile ale documentelor.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_invoice_report,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import unittest

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestInvoiceReportScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_invoice_report"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Demo Comerț SRL")
        env = cls.env
        company = env.company
        admin = env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})

        # Raportul „în limba companiei" citește limba partenerului companiei — fără ea, documentul
        # ar ieși în engleză, deși interfața e în română.
        company.partner_id.lang = "ro_RO"
        # Opțiunile de raport ale modulului, ca factura tipărită să le arate.
        company.write(
            {
                "show_invoice_delegate": True,
                "index_line_on_invoice": True,
                "show_total_amount_with_taxes": True,
            }
        )

        cls.cash_journal = cls.company_data["default_journal_cash"]
        cls.cash_journal.name = "Casa"
        # Județul e obligatoriu la postare când e instalat modulul de e-Factura din localizare.
        state_ab = env["res.country.state"].search([("code", "=", "AB"), ("country_id.code", "=", "RO")], limit=1)
        cls.customer = env["res.partner"].create(
            {
                "name": "Ionescu Maria",
                "is_company": False,
                "country_id": env.ref("base.ro").id,
                "state_id": state_ab.id,
                "street": "Strada Zorilor 12",
                "city": "Alba Iulia",
                "zip": "510001",
            }
        )
        cls.delegate = env["res.partner"].create({"name": "Vasile Pop", "is_company": False, "function": "Delegat"})
        today = fields.Date.context_today(env.user)

        # 1. Factură de client postată, cu delegat și mijloc de transport (pașii 2 și 3)
        product = env["product.product"].create({"name": "Ciment 40 kg", "list_price": 32.0})
        cls.invoice = env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.customer.id,
                "invoice_date": today,
                "date": today,
                "delegate_id": cls.delegate.id,
                "mean_transp": "B 123 XYZ",
                "invoice_line_ids": [
                    (0, 0, {"product_id": product.id, "quantity": 10, "price_unit": 32.0}),
                    (0, 0, {"product_id": product.id, "quantity": 4, "price_unit": 85.0}),
                ],
            }
        )
        # Întocmitorul apare pe document; userul tehnic de test nu are ce căuta într-o fișă.
        cls.invoice.invoice_user_id = admin
        cls.invoice.action_post()

        # 2. Plată în numerar către o persoană fizică → dispoziție de plată, cod 14-4-4 (pașii 4 și 5)
        cls.payment_out = env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "customer",
                "partner_id": cls.customer.id,
                "amount": 320.0,
                "journal_id": cls.cash_journal.id,
                "date": today,
                "memo": "Restituire contravaloare marfă returnată",
            }
        )
        cls.payment_out.action_post()

        # 3. Încasare în numerar → chitanță / dispoziție de încasare, cod 14-4-1 (pasul 6)
        cls.payment_in = env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": cls.customer.id,
                "amount": 660.0,
                "journal_id": cls.cash_journal.id,
                "date": today,
                "memo": "Încasare parțială factură",
            }
        )
        cls.payment_in.action_post()

        env.flush_all()

    def test_capture_fise(self):
        self.capture_screenshots(
            [
                # 1. Factura cu delegatul și mijlocul de transport completate
                {
                    "url": f"id={self.invoice.id}&model=account.move&view_type=form",
                    "name": "01_factura_delegat.png",
                    "wait": ".o_form_view",
                    "click_tab": "Alte informații",
                    "highlight": ["div[name='delegate_id']", "div[name='mean_transp']"],
                    "settle": 2000,
                },
                # 2. Factura tipărită în limba companiei
                self.report_shot(
                    "l10n_ro_invoice_report.report_invoice_company_language",
                    self.invoice,
                    "02_factura_tiparita.png",
                ),
                # 3. Plata în numerar, postată
                {
                    "url": f"id={self.payment_out.id}&model=account.payment&view_type=form",
                    "name": "03_plata_numerar.png",
                    "wait": ".o_form_view",
                    "settle": 2000,
                },
                # 4. Dispoziția de plată către casierie (cod 14-4-4)
                self.report_shot(
                    "l10n_ro_invoice_report.report_payment",
                    self.payment_out,
                    "04_dispozitie_plata.png",
                ),
                # 5. Chitanța / dispoziția de încasare (cod 14-4-1)
                self.report_shot(
                    "l10n_ro_invoice_report.report_payment",
                    self.payment_in,
                    "05_chitanta_incasare.png",
                ),
            ],
            hide_systray=True,
        )
