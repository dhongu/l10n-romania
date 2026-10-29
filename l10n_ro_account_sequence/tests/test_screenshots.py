# © 2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Numerotarea documentelor de casă" — generate în timpul
# testelor, în limba RO, pe planul de conturi RO.
#
# Seedează, în jurnalul de casă al planului RO (5311), câte o plată pentru fiecare tip de
# document: chitanță client (CH), chitanță furnizor (PL), dispoziție de plată (DP) și dispoziție
# de încasare (DI), plus o a doua chitanță client, ca numerotarea separată să se vadă în listă.
# O plată către furnizor rămâne în ciornă, pentru ecranul de introducere.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i deltatech_doc_screenshots -u l10n_ro_account_sequence \
#       --test-tags=/l10n_ro_account_sequence:TestCashSequenceScreenshots --stop-after-init
import json
import unittest

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.deltatech_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestCashSequenceScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_account_sequence"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("deltatech_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Demo Casa SRL")
        env = cls.env
        company = env.company
        env.ref("base.user_admin").write({"company_ids": [(4, company.id)], "company_id": company.id})

        cls.date = fields.Date.today().replace(day=1) - relativedelta(months=1)
        # jurnalul de casă din planul RO (cont 5311); altfel, cel creat de clasa comună
        cls.cash_journal = (
            env["account.journal"].search(
                [("type", "=", "cash"), ("company_id", "=", company.id), ("default_account_id.code", "=like", "5311%")],
                order="sequence, id",
                limit=1,
            )
            or cls.company_data["default_journal_cash"]
        )
        # numele apare în capturi; codul jurnalului (CSH1) rămâne în numărul documentului
        cls.cash_journal.name = "Casa în lei"
        # metoda de plată apare în formular și în eticheta liniilor notei
        lines = cls.cash_journal.inbound_payment_method_line_ids | cls.cash_journal.outbound_payment_method_line_ids
        lines.name = "Numerar"
        ro = env.ref("base.ro").id
        cls.customer = env["res.partner"].create({"name": "Client Demo SRL", "country_id": ro})
        cls.vendor = env["res.partner"].create({"name": "Furnizor Birotică SRL", "country_id": ro})

        def pay(payment_type, partner_type, partner, amount, day, memo, post=True):
            payment = env["account.payment"].create(
                {
                    "payment_type": payment_type,
                    "partner_type": partner_type,
                    "partner_id": partner.id,
                    "amount": amount,
                    "date": cls.date + relativedelta(days=day),
                    "journal_id": cls.cash_journal.id,
                    "memo": memo,
                }
            )
            if post:
                payment.action_post()
            return payment

        cls.receipt = pay("inbound", "customer", cls.customer, 1500.0, 2, "Încasare factură")
        pay("outbound", "supplier", cls.vendor, 380.0, 3, "Plată rechizite, chitanța furnizorului nr. 245")
        pay("inbound", "customer", cls.customer, 620.0, 5, "Încasare factură")
        pay("outbound", "customer", cls.customer, 200.0, 6, "Restituire avans client")
        pay("inbound", "supplier", cls.vendor, 75.0, 8, "Restituire de la furnizor")
        cls.draft_supplier = pay(
            "outbound", "supplier", cls.vendor, 450.0, 9, "Plată toner, chitanța furnizorului nr. 251", post=False
        )

        cls.act_journals = env.ref("account.action_account_journal_form").id
        cls.act_payments = env.ref("account.action_account_payments").id
        cls.act_payments_payable = env.ref("account.action_account_payments_payable").id

    def test_capture_fise(self):
        cash_payments = [("journal_id", "=", self.cash_journal.id)]
        list_view = self.env.ref("account.view_account_payment_tree").id
        self.capture_screenshots(
            [
                # 1. Jurnalul de casă: metodele de plată duc direct în contul casei (5311)
                {
                    "url": f"action={self.act_journals}&id={self.cash_journal.id}&model=account.journal&view_type=form",
                    "name": "01_jurnal_casa_cont.png",
                    "wait": ".o_form_view",
                    "click_tab": "Plăți de Primit",
                    "highlight": ["div[name='inbound_payment_method_line_ids'] td[name='payment_account_id']"],
                    "settle": 2000,
                },
                # 2. Plata către furnizor, în ciornă: tipul propus automat „Chitanță furnizor"
                {
                    "url": f"action={self.act_payments_payable}&id={self.draft_supplier.id}"
                    "&model=account.payment&view_type=form",
                    "name": "02_plata_ciorna_tip.png",
                    "wait": ".o_form_view",
                    "highlight": [
                        "div[name='journal_id']",
                        "div[name='l10n_ro_cash_document_type']",
                        "button[name='action_post']",
                    ],
                    "settle": 2000,
                },
                # 3. Chitanța client confirmată: numărul CH...
                {
                    "url": f"action={self.act_payments}&id={self.receipt.id}&model=account.payment&view_type=form",
                    "name": "03_chitanta_client.png",
                    "wait": ".o_form_view",
                    "highlight": ["div[name='name']", "div[name='l10n_ro_cash_document_type']"],
                    "settle": 2000,
                },
                # 4. Plățile prin casă grupate pe tip: fiecare tip are numerotarea lui
                {
                    "url": f"action={self.act_payments}",
                    "name": "04_plati_grupate_tip.png",
                    "wait": ".o_list_view",
                    "eval": (
                        "async () => { const sleep = (ms) => new Promise((r) => setTimeout(r, ms));"
                        "await odoo.__WOWL_DEBUG__.root.env.services.action.doAction({"
                        "type: 'ir.actions.act_window', res_model: 'account.payment', "
                        f"domain: {json.dumps(cash_payments)}, views: [[{list_view}, 'list'], [false, 'form']], "
                        "context: {group_by: ['l10n_ro_cash_document_type']}, "
                        "name: 'Încasări'}, {clearBreadcrumbs: true});"
                        "await sleep(1500);"
                        "for (const row of document.querySelectorAll('.o_group_header')) {"
                        " row.click(); await sleep(400); } }"
                    ),
                    "eval_wait": 4000,
                    "full": True,
                    "settle": 2000,
                },
                # 5. Nota contabilă a chitanței: tipul documentului de casă și documentul justificativ
                dict(
                    self.account_move_shot(self.receipt.move_id, "05_nota_chitanta.png"),
                    highlight=["div[name='l10n_ro_cash_document_type']", "div[name='l10n_ro_document_type']"],
                    settle=2000,
                ),
            ],
            hide_systray=True,
        )
