# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „e-Factura automatizată" — generate în RO.
#
# Seedează parteneri și facturi fictive în stările e-Factura întâlnite în flux (trimisă,
# neindexată, respinsă, validată), mesaje SPV pentru tabloul de bord și raportul cron-ului de
# trimitere. Nu se apelează ANAF: stările se scriu direct prin documentele e-Factura.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_efactura_enhancement,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_efactura_enhancement:TestEfacturaEnhancementScreenshots --stop-after-init
import unittest

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None

LONG_DESCRIPTION = (
    "Servicii de implementare ERP — configurare module Vânzări, Achiziții, Stocuri și "
    "Contabilitate, migrarea datelor din sistemul vechi, instruirea utilizatorilor cheie și "
    "suport la punerea în producție, conform contractului nr. 145/2026"
)

# Deschide coloanele opționale ale liniilor de factură și le bifează pe cele de lungime.
SHOW_LENGTH_COLUMNS = """
    async () => {
        const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
        const list = document.querySelector("div[name='invoice_line_ids']");
        const toggle = list && list.querySelector('.o_optional_columns_dropdown_toggle');
        if (!toggle) { return; }
        toggle.click();
        await sleep(600);
        for (const item of document.querySelectorAll('.o-dropdown--menu .dropdown-item')) {
            if (/Lungime|length/.test(item.textContent)) {
                const input = item.querySelector('input');
                if (input && !input.checked) { input.click(); await sleep(400); }
            }
        }
        await sleep(400);
        // închide meniul de coloane, ca să nu acopere liniile
        toggle.click();
        await sleep(600);
    }
"""

# Bifează trei facturi confirmate din listă și deschide meniul Acțiuni.
OPEN_ACTIONS_MENU = """
    async () => {
        const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
        const rows = [...document.querySelectorAll('.o_data_row')]
            .filter((row) => /INV\\//.test(row.textContent)).slice(0, 3);
        for (const row of rows) {
            row.querySelector('.o_list_record_selector').click();
            await sleep(300);
        }
        await sleep(800);
        // Odoo 20: meniul „Acțiuni" din bara de control, cu iconiță oi (nu fa-cog)
        const actions = [...document.querySelectorAll('.o_control_panel button.dropdown-toggle')]
            .find((btn) => /Acțiuni|Actions/.test(btn.textContent));
        if (actions) { actions.click(); }
        await sleep(800);
    }
"""

# Deschide tabloul „eFactura SPV" din bara laterală a tablourilor de bord.
OPEN_EFACTURA_DASHBOARD = """
    async () => {
        const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
        for (let i = 0; i < 50; i++) {
            const item = [...document.querySelectorAll('.o_search_panel li, .o_spreadsheet_dashboard_action li, aside li')]
                .find((el) => el.textContent.trim() === 'eFactura SPV');
            if (item) { (item.querySelector('a, header, div') || item).click(); break; }
            await sleep(200);
        }
        await sleep(4000);
    }
"""

SCROLL_TO_SETTINGS = """
    () => {
        const el = document.querySelector('#l10n_ro_spv_cron_no_email');
        if (el) { el.scrollIntoView({block: 'center'}); }
    }
"""


@tagged("-at_install", "post_install", "fise_screenshots")
class TestEfacturaEnhancementScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_efactura_enhancement"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        company = cls.prepare_ro_company(name="RO Company")
        env = cls.env
        admin = env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        company.partner_id.lang = "ro_RO"
        company.write(
            {
                "l10n_ro_edi_access_token": "demo-token",
                "l10n_ro_spv_cron_report_email": "contabilitate@example.ro",
            }
        )

        ro = env.ref("base.ro")
        state_cj = env["res.country.state"].search([("code", "=", "CJ"), ("country_id", "=", ro.id)], limit=1)
        state_b = env["res.country.state"].search([("code", "=", "B"), ("country_id", "=", ro.id)], limit=1)
        Partner = env["res.partner"].with_context(no_vat_validation=True)
        cls.client_srl = Partner.create(
            {
                "name": "Alfa Distribuție SRL",
                "is_company": True,
                "vat": "RO30834857",
                "street": "Bd. Unirii 20",
                "city": "Sector 1",
                "state_id": state_b.id,
                "country_id": ro.id,
                "email": "facturi@alfa.example.ro",
            }
        )
        cls.client_pf = Partner.create(
            {
                "name": "Ion Popescu",
                "street": "Str. Eroilor 5",
                "city": "Florești",
                "state_id": state_cj.id,
                "country_id": ro.id,
            }
        )
        cls.client_no_street = Partner.create(
            {
                "name": "Beta Construct SRL",
                "is_company": True,
                "vat": "RO14399840",
                "city": "Cluj-Napoca",
                "state_id": state_cj.id,
                "country_id": ro.id,
            }
        )
        cls.client_de = Partner.create(
            {
                "name": "Gamma Handel GmbH",
                "is_company": True,
                "street": "Hauptstraße 1",
                "city": "Berlin",
                "country_id": env.ref("base.de").id,
            }
        )
        # Serviciu: venitul se înregistrează în 704 „Venituri din servicii prestate", nu în 707.
        income_704 = env["account.account"].search(
            [("code", "=like", "704%"), ("company_ids", "in", company.ids)], limit=1
        )
        cls.product = env["product.product"].create(
            {
                "name": "Consultanță ERP",
                "default_code": "CONS-ERP",
                "type": "service",
                "list_price": 1500.0,
                "property_account_income_id": income_704.id,
            }
        )

        yesterday = fields.Date.today() - relativedelta(days=1)
        cls.inv_lines = cls._invoice(cls.client_srl, yesterday, name=LONG_DESCRIPTION, post=False, price=4800.0)
        cls.inv_blocked = cls._invoice(cls.client_no_street, yesterday, post=False)
        cls.inv_sent = cls._invoice(cls.client_srl, yesterday)
        cls.inv_validated = cls._invoice(cls.client_pf, yesterday)
        cls.inv_not_indexed = cls._invoice(cls.client_srl, yesterday)
        cls.inv_refused = cls._invoice(cls.client_srl, yesterday - relativedelta(days=1))
        cls._invoice(cls.client_de, yesterday)
        cls._invoice(cls.client_pf, yesterday)

        Document = env["l10n_ro_edi.document"].sudo()
        Document.create({"invoice_id": cls.inv_sent.id, "state": "invoice_sent"})
        cls.inv_sent.l10n_ro_edi_index = "5012345671"
        Document.create({"invoice_id": cls.inv_validated.id, "state": "invoice_validated"})
        Document.create({"invoice_id": cls.inv_not_indexed.id, "state": "invoice_sent"})
        cls.inv_not_indexed.l10n_ro_edi_state = "invoice_not_indexed"
        Document.create(
            {
                "invoice_id": cls.inv_refused.id,
                "state": "invoice_refused",
                "message": "E-Factura respinsă de SPV: BR-CO-09 — codul de TVA al cumpărătorului (BT-48) "
                "nu are un prefix de țară valid.",
            }
        )

        # Mesajele SPV din tabloul de bord (ultimele zile, pe stări).
        Message = env["l10n.ro.message.spv"].sudo()
        now = fields.Datetime.now()
        for days, state, count in (
            (1, "done", 6),
            (1, "invoice", 2),
            (3, "downloaded", 3),
            (5, "error", 1),
            (12, "draft", 2),
        ):
            for index in range(count):
                Message.create(
                    {
                        "name": f"50{days}{index:02d}{state[:2].upper()}",
                        "message_type": "in_invoice",
                        "date": now - relativedelta(days=days, hours=index),
                        "state": state,
                        "company_id": company.id,
                    }
                )

        # Raportul unei rulări a cron-ului de trimitere (stările de mai sus).
        Move = env["account.move"]
        attempted = cls.inv_sent | cls.inv_not_indexed
        Move._l10n_ro_spv_send_cron_report(
            company,
            {
                "candidates": attempted,
                "attempted": attempted,
                "validated": Move,
                "pending": cls.inv_sent,
                "failed_now": cls.inv_not_indexed,
                "retrying": Move,
                "exhausted": Move,
            },
        )
        cls.report_mail = env["mail.mail"].sudo().search([("subject", "like", "Raport e-Factura SPV")], limit=1)

        # Acțiuni de listă filtrate, ca ecranele să arate doar înregistrările modulului.
        Action = env["ir.actions.act_window"].sudo()
        cls.act_params = Action.create(
            {
                "name": "Parametri de sistem",
                "res_model": "ir.config_parameter",
                "view_mode": "list,form",
                "domain": "[('key', 'like', 'efactura.')]",
            }
        )
        cls.act_crons = Action.create(
            {
                "name": "Acțiuni planificate",
                "res_model": "ir.cron",
                "view_mode": "list,form",
                "domain": "[('cron_name', 'ilike', 'factura')]",
            }
        )
        cls.dashboard = env.ref("l10n_ro_efactura_enhancement.spreadsheet_dashboard_efactura")
        env.flush_all()

    @classmethod
    def _invoice(cls, partner, date, name=None, post=True, price=1500.0):
        line = {"product_id": cls.product.id, "quantity": 1, "price_unit": price}
        if name:
            line["name"] = name
        move = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_date": date,
                "date": date,
                "invoice_line_ids": [(0, 0, line)],
            }
        )
        if post:
            move.action_post()
        return move

    def _invoice_url(self, move):
        action = self.env.ref("account.action_move_out_invoice_type").id
        return f"action={action}&id={move.id}&model=account.move&view_type=form"

    def test_capture_fise(self):
        out_invoices = self.env.ref("account.action_move_out_invoice_type").id
        settings = self.env.ref("account.action_account_config").id
        mail_body = self.report_mail.body_html or ""
        self.capture_screenshots(
            [
                {
                    "url": f"action={settings}",
                    "name": "01_setari_efactura_spv.png",
                    "wait": "#l10n_ro_spv_cron_no_email",
                    "timeout": 60000,
                    "eval": SCROLL_TO_SETTINGS,
                    "highlight": [
                        "#l10n_ro_spv_cron_no_email",
                        "#l10n_ro_spv_cron_report_email",
                        "#l10n_ro_edi_no_auto_bill",
                    ],
                    "settle": 2000,
                },
                {
                    "url": f"action={self.act_params.id}&view_type=list",
                    "name": "02_parametri_sistem.png",
                    "wait": ".o_list_view",
                },
                {
                    "url": self._invoice_url(self.inv_lines),
                    "name": "03_linii_lungime_descriere.png",
                    "wait": ".o_form_view",
                    "eval": SHOW_LENGTH_COLUMNS,
                    "eval_wait": 1500,
                    "settle": 2000,
                },
                {
                    "url": self._invoice_url(self.inv_blocked),
                    "name": "04_blocaj_adresa_partener.png",
                    "wait": ".o_form_view",
                    "click_btn": "button[name='action_post']",
                    "wait_after": ".modal .modal-body",
                    "settle": 2500,
                },
                {
                    "url": f"action={out_invoices}&view_type=list",
                    "name": "05_lista_actiune_trimite_spv.png",
                    "wait": ".o_list_view",
                    "eval": OPEN_ACTIONS_MENU,
                    "eval_wait": 1500,
                    "highlight": ".o-dropdown--menu .dropdown-item:has-text('Trimite în SPV')",
                    "settle": 1500,
                },
                {
                    "url": f"action={self.act_crons.id}&view_type=list",
                    "name": "06_cronuri_efactura.png",
                    "wait": ".o_list_view",
                },
                {
                    "html": (
                        "<html><body style='font-family:Arial,sans-serif;background:#fff;"
                        f"padding:24px;max-width:900px'>{mail_body}</body></html>"
                    ),
                    "name": "07_raport_cron_spv.png",
                },
                {
                    "url": self._invoice_url(self.inv_not_indexed),
                    "name": "08_factura_neindexata.png",
                    "wait": ".o_form_view",
                    "click_tab": "E- Factură",
                    "highlight": "button[name='action_l10n_ro_edi_fetch_status']",
                    "settle": 2000,
                },
                {
                    "url": self._invoice_url(self.inv_refused),
                    "name": "09_factura_respinsa_retrimite.png",
                    "wait": ".o_form_view",
                    "click_tab": "E- Factură",
                    "highlight": "button[name='action_send_to_spv_only']",
                    "settle": 2000,
                },
                {
                    "url": f"action=spreadsheet_dashboard.ir_actions_dashboard_action&dashboard_id={self.dashboard.id}",
                    "name": "10_dashboard_efactura_spv.png",
                    "wait": ".o-spreadsheet",
                    "timeout": 60000,
                    "eval": OPEN_EFACTURA_DASHBOARD,
                    "eval_wait": 2000,
                    "settle": 3000,
                },
            ]
        )
