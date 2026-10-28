# Capturi de ecran pentru fișa „Date obligatorii e-Factura la clientul creat în POS".
# Seedează un punct de vânzare cu sesiune deschisă; fiecare captură deschide POS-ul și parcurge
# din browser pașii casierului (Client → Creează → formularul de partener). Răspunsul ANAF este
# simulat, ca rularea să nu depindă de serviciul ANAF.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> \
#       -i l10n_ro_pos_partner_efactura,l10n_ro_partner_create_by_vat,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import json
import unittest
from unittest.mock import patch

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None

try:
    from odoo.addons.l10n_ro_partner_create_by_vat.models.res_partner import ResPartner as AnafPartner
    from odoo.addons.l10n_ro_partner_create_by_vat.tests.anaf_data import ANAF_TEST_DATA
except ImportError:
    AnafPartner = None

ANAF_CUI = "30834857"
ANAF_DOWN = "Serviciul web ANAF nu funcționează. Excepție ridicată: Read timed out. (read timeout=30)"

# Funcții JS comune: așteptare, click și completarea câmpurilor din formularul de partener.
JS_HELPERS = """
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    const wait = async (sel, timeout = 15000) => {
        const start = Date.now();
        while (Date.now() - start < timeout) {
            const el = document.querySelector(sel);
            if (el) { return el; }
            await sleep(100);
        }
        throw new Error('Nu apare: ' + sel);
    };
    const click = async (sel) => { (await wait(sel)).click(); await sleep(500); };
    const fill = async (name, value) => {
        const input = await wait(`.modal div[name='${name}'] input`);
        input.focus();
        input.value = value;
        input.dispatchEvent(new Event('input', {bubbles: true}));
        input.dispatchEvent(new Event('change', {bubbles: true}));
        input.blur();
        await sleep(800);
    };
    const pick = async (name, value) => {
        const input = await wait(`.modal div[name='${name}'] input`);
        input.focus();
        input.value = value;
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await click('.modal .o-autocomplete--dropdown-item a');
        await sleep(500);
    };
    const openNewPartner = async () => {
        await click('.product-screen button.set-partner');
        await wait('.partner-list');
        await click('.modal-header button.btn-primary');
        await wait('.modal .o_form_view');
        await sleep(800);
    };
    const asCompany = async () => {
        await click(".modal div[name='company_type'] input[data-value='company']");
        await sleep(500);
    };
    const save = async () => { await click('.modal .o_form_button_save'); await sleep(1500); };
"""


# La deschidere POS-ul arată ecranul „Deschide casa”; trecem de el spre ecranul de vânzare.
OPEN_REGISTER = """
    const openBtn = document.querySelector('.open-register-btn');
    if (openBtn) { openBtn.click(); }
    await wait('.product-screen', 30000);
    await sleep(1000);
"""


def _js(body):
    return "async () => {" + JS_HELPERS + OPEN_REGISTER + body + "}"


@tagged("-at_install", "post_install", "fise_screenshots")
class TestPosPartnerEfacturaScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_pos_partner_efactura"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        if AnafPartner is None:
            raise unittest.SkipTest("l10n_ro_partner_create_by_vat indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Magazin Demo SRL")
        company = cls.env.company
        admin = cls.env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        pos_manager = cls.env.ref("point_of_sale.group_pos_manager")
        admin.group_ids = [(4, pos_manager.id)]
        cls.env.user.sudo().group_ids = [(4, pos_manager.id)]
        env = cls.env

        cash_journal = env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", company.id)], limit=1
        ) or env["account.journal"].create(
            {"name": "Numerar POS", "type": "cash", "code": "CSHRO", "company_id": company.id}
        )
        payment_method = env["pos.payment.method"].create(
            {"name": "Numerar", "journal_id": cash_journal.id, "company_id": company.id}
        )
        cls.config = env["pos.config"].create(
            {
                "name": "Magazin Centru",
                "company_id": company.id,
                "payment_method_ids": [Command.set(payment_method.ids)],
            }
        )
        env["product.product"].create(
            {"name": "Cafea boabe 1 kg", "list_price": 89.0, "available_in_pos": True, "type": "consu"}
        )
        cls.config.with_user(admin).open_ui()
        cls.config.current_session_id.set_opening_control(0, "")

    @staticmethod
    def _fake_get_anaf(self, cod, data=False):
        if cod == ANAF_CUI:
            return "", json.loads(json.dumps(ANAF_TEST_DATA[ANAF_CUI]))
        return ANAF_DOWN, {}

    def _pos(self, name, body, highlight=None, settle=1500):
        shot = {
            "path": f"/pos/ui/{self.config.id}",
            "name": name,
            "wait": ".open-register-btn, .product-screen",
            "timeout": 60000,
            "eval": _js(body),
            "eval_wait": 1000,
            "settle": settle,
        }
        if highlight:
            shot["highlight"] = highlight
        return shot

    def test_capture_fise(self):
        address = [".modal div[name='street']", ".modal div[name='city']", ".modal div[name='state_id']"]
        shots = [
            self._pos(
                "01_pos_lista_clienti.png",
                "await click('.product-screen button.set-partner'); await wait('.partner-list');",
                highlight=".modal-header button.btn-primary",
            ),
            self._pos(
                "02_formular_partener_obligatorii.png",
                "await openNewPartner(); await asCompany();",
                highlight=address + [".modal div[name='country_id']", ".modal div[name='vat']"],
            ),
            self._pos(
                "03_preluare_anaf.png",
                f"await openNewPartner(); await asCompany(); await fill('vat', '{ANAF_CUI}'); await sleep(1500);",
                highlight=[".modal div[name='vat']"] + address,
            ),
            self._pos(
                "04_anaf_indisponibil_manual.png",
                "await openNewPartner(); await asCompany(); await fill('vat', '12345678'); await sleep(1500);",
                highlight=".modal-content:has-text('Serviciul web ANAF')",
            ),
            self._pos(
                "05_date_lipsa.png",
                "await openNewPartner(); await fill('name', 'Ionescu Maria'); await save();",
                highlight=address,
            ),
            self._pos(
                "06_bucuresti_sector.png",
                "await openNewPartner(); await fill('name', 'Popescu Andrei');"
                " await fill('street', 'Str. Lipscani 10'); await fill('city', 'București');"
                " await pick('state_id', 'București'); await save();",
                settle=2500,
            ),
            self._pos(
                "07_client_pe_comanda.png",
                f"await openNewPartner(); await asCompany(); await fill('vat', '{ANAF_CUI}');"
                " await sleep(1500); await save(); await wait('.product-screen'); await sleep(1500);",
                highlight=".product-screen button.set-partner",
            ),
        ]
        with patch.object(AnafPartner, "_get_Anaf", self._fake_get_anaf):
            self.capture_screenshots(shots, hide_systray=True)
