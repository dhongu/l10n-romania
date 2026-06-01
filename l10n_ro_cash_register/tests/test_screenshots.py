# Copyright (C) 2025 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
#
# Capturi de ecran pentru fișa Registrului de casă — generate în timpul testelor, în limba RO.
#
# Folosește mixinul reutilizabil `ScreenshotCase` din `l10n_ro_doc_screenshots` (import defensiv:
# dacă tooling-ul lipsește, testul nu se definește). Seedează un jurnal de casă, registre și câteva
# operațiuni (încasări/plăți) pe planul de conturi RO.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_cash_register \
#       --test-tags=fise_screenshots --stop-after-init
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestCashRegisterScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_cash_register"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.prepare_ro_company(name="Demo Registru Casă SRL")  # RON, drepturi contabile + limba RO
        cls.env.company.chart_template = "ro"
        # admin trebuie să aibă compania de test ca firmă activă (altfel jurnalul nu e accesibil în UI)
        cls.env.ref("base.user_admin").write(
            {"company_ids": [(4, cls.env.company.id)], "company_id": cls.env.company.id}
        )

        cls.cash_journal = cls.env["account.journal"].create({"name": "Casă lei", "code": "CASA", "type": "cash"})
        cls.partner = cls.env["res.partner"].create(
            {"name": "Client Numerar SRL", "country_id": cls.env.ref("base.ro").id}
        )

        last_month = fields.Date.today() - relativedelta(months=1)
        cls.date_open = last_month.replace(day=2)
        cls.date_reg = last_month.replace(day=3)

        # sold inițial + mișcări pe ziua registrului (încasare client, plată furnizor)
        cls._cash_op(cls.date_open, 1000.0, "in", "Sold inițial numerar")
        cls._cash_op(cls.date_reg, 500.0, "in", "Încasare client")
        cls._cash_op(cls.date_reg, 200.0, "out", "Plată furnizor")

        # generează registrele zilnice din mișcările postate și reîmprospătează soldurile
        cls.cash_journal.generate_missing_cash_register()
        cls.register = cls.env["l10n.ro.cash.register"].search(
            [("journal_id", "=", cls.cash_journal.id), ("date", "=", cls.date_reg)], limit=1
        )
        cls.env["l10n.ro.cash.register"].search([("journal_id", "=", cls.cash_journal.id)]).action_refresh()

        cls.act_list = cls.env.ref("l10n_ro_cash_register.action_cash_register").id

    @classmethod
    def _cash_op(cls, date, amount, operation, description):
        wizard = cls.env["l10n.ro.cash.register.operation"].create(
            {
                "journal_id": cls.cash_journal.id,
                "date": date,
                "amount": amount,
                "operation": operation,
                "description": description,
                "partner_id": cls.partner.id,
                "counterpart_account_id": cls.env.company.transfer_account_id.id,
            }
        )
        wizard.action_confirm()

    def test_capture_fise(self):
        reg = self.register.id
        self.capture_screenshots(
            [
                # 1. Jurnalul de casă (din care se accesează registrul)
                {
                    "url": f"id={self.cash_journal.id}&model=account.journal&view_type=form",
                    "name": "01_jurnal_cash.png",
                    "wait": ".o_form_view",
                    "settle": 2000,
                },
                # 2. Lista registrelor de casă
                {
                    "url": f"action={self.act_list}",
                    "name": "02_lista_registre.png",
                    "wait": ".o_list_view",
                    "settle": 2000,
                },
                # 3. Formularul registrului cu butoanele Refresh / Add Receipt / Add Payment / Operation
                {
                    "url": f"action={self.act_list}&id={reg}&view_type=form",
                    "name": "03_formular_registru.png",
                    "wait": ".o_form_view",
                    "settle": 2000,
                    "full": True,
                },
                # 4. Wizardul de operațiune (deschis din formular cu butonul Operation)
                {
                    "url": f"action={self.act_list}&id={reg}&view_type=form",
                    "name": "04_wizard_operatiune.png",
                    "wait": ".o_form_view",
                    "settle": 1500,
                    "click_btn": "button[name='action_operation']",
                    "wait_after": ".modal-content",
                    "trim": False,
                },
                # 5. Raportul PDF „Registru de casă"
                {
                    "path": f"/report/html/l10n_ro_cash_register.report_cash_register/{reg}",
                    "name": "05_raport_pdf.png",
                    "wait": "body",
                    "settle": 2000,
                    "full": True,
                    "hide_chatter": False,
                },
            ],
            viewport=(1500, 1000),
        )
