# Copyright (C) 2025 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
#
# Capturi de ecran pentru fișa Registrului de casă — generate în timpul testelor, în limba RO.
#
# Folosește mixinul reutilizabil `ScreenshotCase` din `l10n_ro_doc_screenshots` (import defensiv:
# dacă tooling-ul lipsește, testul nu se definește). Seedează un jurnal de casă, trei zile de
# operațiuni pe planul de conturi RO (alimentare din bancă, încasare client, plată furnizor,
# avans de trezorerie) și o zi deja închisă, apoi parcurge închiderea zilei, blocarea unei
# postări în ziua închisă, redeschiderea și monetarul zilei 3 (numărare pe cupiuri, lipsă de casă).
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_cash_register,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import unittest

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
        # Tooling-ul de capturi (`l10n_ro_doc_screenshots`) trăiește în arborele `l10n_ro_ent`
        # și poate lipsi de pe addons_path (ex. CI-ul standalone `l10n-romania`). Fără el,
        # `ScreenshotCase` e None, deci sărim testul în loc să eșueze cu AttributeError.
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots (tooling capturi) indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Demo Registru Casă SRL")  # RON, drepturi contabile + limba RO
        cls.env.company.chart_template = "ro"
        # admin trebuie să aibă compania de test ca firmă activă (altfel jurnalul nu e accesibil în UI)
        cls.env.ref("base.user_admin").write(
            {"company_ids": [(4, cls.env.company.id)], "company_id": cls.env.company.id}
        )

        chart = cls.env["account.chart.template"].with_company(cls.env.company)
        cls.acc_transfer = chart.ref("pcg_581")  # 581 Viramente interne
        cls.acc_supplier = chart.ref("pcg_4011")  # 401 Furnizori
        cls.acc_advance = chart.ref("pcg_542")  # 542 Avansuri de trezorerie

        # Utilizatorii care închid și redeschid ziua: numele lor apar în „Închisă de" și în istoric.
        # Limba RO pe utilizator: mesajul de redeschidere se scrie în limba celui care redeschide.
        groups = [cls.env.ref("base.group_user").id, cls.env.ref("account.group_account_manager").id]
        user_vals = {
            "group_ids": [(6, 0, groups)],
            "company_id": cls.env.company.id,
            "company_ids": [(6, 0, cls.env.company.ids)],
            "lang": "ro_RO",
        }
        users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.cashier = users.create({"name": "Maria Popescu", "login": "maria.popescu", **user_vals})
        cls.chief_accountant = users.create({"name": "Elena Dumitrescu", "login": "elena.dumitrescu", **user_vals})

        # Plusurile și minusurile de casă pe conturile din planul RO, nu pe rezerva generică 999xxx
        cls.cash_journal = cls.env["account.journal"].create(
            {
                "name": "Casa lei",
                "code": "CASA",
                "type": "cash",
                "profit_account_id": chart.ref("pcg_7588").id,
                "loss_account_id": chart.ref("pcg_65881").id,
            }
        )
        cls.tax_sale = chart.ref("tvac_21")
        cls.tax_purchase = chart.ref("tvad_21")
        ro = cls.env.ref("base.ro").id
        cls.client = cls.env["res.partner"].create({"name": "Alfa Distribuție SRL", "country_id": ro})
        cls.supplier = cls.env["res.partner"].create({"name": "Papetăria Centrală SRL", "country_id": ro})
        cls.employee = cls.env["res.partner"].create({"name": "Ionescu Andrei", "country_id": ro})

        last_month = fields.Date.today() - relativedelta(months=1)
        cls.date_inv = last_month.replace(day=1)
        cls.date_d1 = last_month.replace(day=2)
        cls.date_d2 = last_month.replace(day=3)
        cls.date_d3 = last_month.replace(day=4)

        # Facturile achitate prin casă (bază + TVA 21% = sumele rotunde din registru)
        inv_client_1 = cls._invoice("out_invoice", cls.client, 413.22, cls.tax_sale, "Marfă livrată")
        bill_supplier = cls._invoice("in_invoice", cls.supplier, 165.29, cls.tax_purchase, "Rechizite birou", "PC-2291")
        inv_client_2 = cls._invoice("out_invoice", cls.client, 247.93, cls.tax_sale, "Marfă livrată")

        # Ziua 1: alimentarea casei din bancă (5311 = 581) — operațiune fără factură, din wizard
        cls._cash_op(cls.date_d1, 1000.0, "in", "Alimentare casă din bancă (CEC 0045)", None, cls.acc_transfer)
        # registrul zilei 1 se deschide în ziua lui (numerotarea registrelor urmează ordinea creării);
        # următoarele se creează singure la postarea plăților pe casierie
        cls.env["l10n.ro.cash.register"].create({"journal_id": cls.cash_journal.id, "date": cls.date_d1})
        # Ziua 2: încasarea facturii clientului (5311 = 4111) și plata furnizorului (401 = 5311),
        # cu butoanele Încasare / Plată (chitanță / dispoziție, lettrare cu factura);
        # avansul de trezorerie (542 = 5311) — fără factură, din wizard
        cls._pay(inv_client_1, cls.date_d2)
        cls._pay(bill_supplier, cls.date_d2)
        cls._cash_op(cls.date_d2, 150.0, "out", "Avans deplasare Cluj", cls.employee, cls.acc_advance)
        # Ziua 3: altă încasare de la client
        cls._pay(inv_client_2, cls.date_d3)

        # generează registrele zilnice din mișcările postate
        cls.cash_journal.generate_missing_cash_register()
        registers = cls.env["l10n.ro.cash.register"].search([("journal_id", "=", cls.cash_journal.id)])
        registers.action_refresh()
        cls.register_d1 = registers.filtered(lambda r: r.date == cls.date_d1)
        cls.register = registers.filtered(lambda r: r.date == cls.date_d2)
        cls.register_d3 = registers.filtered(lambda r: r.date == cls.date_d3)
        # rutina zilnică: ziua precedentă e deja închisă
        cls._as(cls.cashier, cls.register_d1).action_close()

        # O plată uitată, introdusă în ciornă cu data zilei 2 — postarea ei va fi refuzată
        # după ce ziua 2 se închide.
        cls.late_move = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": cls.cash_journal.id,
                "date": cls.date_d2,
                "ref": "Plată factura PC-2297 (înregistrată cu întârziere)",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": cls.acc_supplier.id,
                            "partner_id": cls.supplier.id,
                            "name": "Plată factura PC-2297",
                            "debit": 80.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": cls.cash_journal.default_account_id.id,
                            "partner_id": cls.supplier.id,
                            "name": "Plată factura PC-2297",
                            "credit": 80.0,
                        },
                    ),
                ],
            }
        )

        cls.act_list = cls.env.ref("l10n_ro_cash_register.action_cash_register").id
        cls.act_denominations = cls.env.ref("l10n_ro_cash_register.action_cash_denomination").id

    @classmethod
    def _invoice(cls, move_type, partner, price, tax, label, ref=None):
        invoice = cls.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": partner.id,
                "invoice_date": cls.date_inv,
                "date": cls.date_inv,
                "ref": ref,
                "invoice_line_ids": [
                    (0, 0, {"name": label, "quantity": 1, "price_unit": price, "tax_ids": [(6, 0, tax.ids)]})
                ],
            }
        )
        invoice.action_post()
        return invoice

    @classmethod
    def _pay(cls, invoice, date):
        # limba RO: eticheta liniilor de plată se scrie în limba utilizatorului care plătește
        cls.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids, lang="ro_RO"
        ).create({"journal_id": cls.cash_journal.id, "payment_date": date}).action_create_payments()

    @classmethod
    def _cash_op(cls, date, amount, operation, description, partner, account):
        wizard = cls.env["l10n.ro.cash.register.operation"].create(
            {
                "journal_id": cls.cash_journal.id,
                "date": date,
                "amount": amount,
                "operation": operation,
                "description": description,
                "partner_id": partner.id if partner else False,
                "counterpart_account_id": account.id,
            }
        )
        wizard.action_confirm()

    @classmethod
    def _as(cls, user, records):
        # urmărirea modificărilor e oprită implicit în teste; o repornim ca istoricul
        # registrului să arate închiderea și redeschiderea, ca în producție; limba vine din
        # context (ca în sesiunea web a utilizatorului), nu doar din preferința lui
        return records.with_user(user).with_context(tracking_disable=False, mail_notrack=False, lang=user.lang)

    def _flush_tracking(self):
        # mesajele de urmărire se scriu la commit; în test nu există commit, deci le forțăm
        self.env.flush_all()
        self.env.cr.precommit.run()

    def _register_form(self, name, register=None, **extra):
        shot = {
            "url": f"action={self.act_list}&id={(register or self.register).id}&view_type=form",
            "name": name,
            "wait": ".o_form_view",
            "settle": 2000,
        }
        shot.update(extra)
        return shot

    def test_capture_fise(self):
        viewport = (1500, 820)
        # Partea 1 — ziua 2 este deschisă: operare, tipărire, cererea de închidere.
        self.capture_screenshots(
            [
                # 1. Jurnalul de casă (din care se accesează registrul)
                {
                    "url": f"id={self.cash_journal.id}&model=account.journal&view_type=form",
                    "name": "01_jurnal_cash.png",
                    "wait": ".o_form_view",
                    "settle": 2000,
                },
                # 2. Lista registrelor: ziua 1 închisă, celelalte deschise
                {
                    "url": f"action={self.act_list}",
                    "name": "02_lista_registre.png",
                    "wait": ".o_list_view",
                    "settle": 2000,
                },
                # 3. Formularul registrului zilei 2, deschis, cu butoanele de operare
                self._register_form(
                    "03_formular_registru.png",
                    full=True,
                    highlight=[
                        "button[name='action_receipt']",
                        "button[name='action_payment']",
                        "button[name='action_operation']",
                    ],
                ),
                # 4. Wizardul de operațiune (deschis din formular cu butonul Operație)
                self._register_form(
                    "04_wizard_operatiune.png",
                    settle=1500,
                    click_btn="button[name='action_operation']",
                    wait_after=".modal-content",
                    trim=False,
                ),
                # 5. Raportul PDF „Registrul de casă"
                {
                    "path": f"/report/html/l10n_ro_cash_register.report_cash_register/{self.register.id}",
                    "name": "05_raport_pdf.png",
                    "wait": "body",
                    "settle": 2000,
                    "full": True,
                    "hide_chatter": False,
                },
                # 6. Închide ziua → dialogul de confirmare
                self._register_form(
                    "06_confirmare_inchidere.png",
                    click_btn="button[name='action_close']",
                    wait_after=".modal-content",
                    trim=False,
                ),
            ],
            viewport=viewport,
        )

        # Partea 2 — ziua 2 închisă: registru înghețat, postare refuzată, cererea de redeschidere.
        self._as(self.cashier, self.register).action_close()
        self._flush_tracking()
        self.capture_screenshots(
            [
                # 7. Registrul închis: sold la închidere, închisă de, închisă la
                self._register_form(
                    "07_registru_inchis.png",
                    full=True,
                    highlight=["div[name='state']", ".o_inner_group:has(div[name='closed_balance'])"],
                ),
                # 8. Postarea unei note pe casă datate în ziua închisă → mesaj de blocare
                {
                    "url": f"id={self.late_move.id}&model=account.move&view_type=form",
                    "name": "08_blocare_postare.png",
                    "wait": ".o_form_view",
                    "click_btn": "button[name='action_post']",
                    "wait_after": ".modal-content",
                    "settle": 3500,
                    "trim": False,
                },
                # 9. Redeschide → dialogul de confirmare
                self._register_form(
                    "09_confirmare_redeschidere.png",
                    click_btn="button[name='action_reopen']",
                    wait_after=".modal-content",
                    trim=False,
                ),
            ],
            viewport=viewport,
        )

        # Partea 3 — ziua 2 redeschisă: urma în istoric.
        self._as(self.chief_accountant, self.register).action_reopen()
        self._flush_tracking()
        self.capture_screenshots(
            [
                # 10. Registrul redeschis, cu mesajul din istoric
                self._register_form("10_registru_redeschis.png", hide_chatter=False),
            ],
            viewport=(1800, 1000),
        )

        # Partea 4 — monetarul zilei 3: sold scriptic 1.450 lei, numărat 1.445 lei (lipsă 5 lei).
        register = self._as(self.cashier, self.register_d3)
        register.action_count_cash()
        counted = {500: 2, 200: 2, 10: 4, 5: 1}
        for line in register.count_line_ids:
            line.quantity = counted.get(line.value, 0)
        self.capture_screenshots(
            [
                # 11. Cupiurile de numerar (Configurare)
                {
                    "url": f"action={self.act_denominations}",
                    "name": "11_cupiuri.png",
                    "wait": ".o_list_view",
                    "settle": 2000,
                },
                # 12. Monetarul pe registrul zilei 3: numărat, sold scriptic, diferență
                self._register_form(
                    "12_monetar_numarare.png",
                    register=self.register_d3,
                    click_tab="Monetar",
                    full=True,
                    highlight=[
                        "button[name='action_record_difference']",
                        ".o_inner_group:has(div[name='count_difference'])",
                    ],
                ),
                # 13. Monetarul tipărit
                {
                    "path": f"/report/html/l10n_ro_cash_register.report_cash_count/{self.register_d3.id}",
                    "name": "13_monetar_pdf.png",
                    "wait": "body",
                    "settle": 2000,
                    "full": True,
                    "hide_chatter": False,
                },
                # 14. Înregistrează diferența → operațiunea de casă precompletată
                self._register_form(
                    "14_inregistrare_diferenta.png",
                    register=self.register_d3,
                    click_btn="button[name='action_record_difference']",
                    wait_after=".modal-content",
                    trim=False,
                ),
            ],
            viewport=viewport,
        )

        # Lipsa se înregistrează pe contul de pierdere al jurnalului; monetarul ajunge la diferență zero.
        action = register.action_record_difference()
        wizard = self.env["l10n.ro.cash.register.operation"].with_context(**action["context"]).create({})
        wizard.action_confirm()
        self.register_d3.action_refresh()
        self.capture_screenshots(
            [
                # 15. Registrul după înregistrarea lipsei: linia de 5 lei, diferență zero
                self._register_form(
                    "15_monetar_inregistrat.png",
                    register=self.register_d3,
                    full=True,
                    highlight=[".o_inner_group:has(div[name='count_difference'])"],
                ),
            ],
            viewport=viewport,
        )
