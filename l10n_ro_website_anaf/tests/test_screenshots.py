# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa consultant „ANAF în formularul de adresă al magazinului", în RO.
# Cererile către ANAF sunt simulate (patch pe `anaf.anaf_lookup`, folosit atât de ruta de căutare,
# cât și de verificarea la salvare): niciun apel real. Clientul din magazin este un utilizator portal
# cu coș deschis, ca în `test_anaf_prefill`.
#
# Rulare:
#   .venv/bin/python odoo/odoo-bin -c odoo.conf -d <db> -u l10n_ro_website_anaf \
#       --test-tags=fise_screenshots/l10n_ro_website_anaf --stop-after-init
import json
import unittest
from unittest.mock import patch

import odoo
from odoo.tests import new_test_user, tagged

from .. import anaf
from ..controllers import main

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None

#: codurile fiscale din capturi (cifră de control corectă) și răspunsul simulat al ANAF
CUI_ACTIVA = "18547290"
CUI_INACTIVA = "14399840"
CUI_RADIATA = "37024165"
CUI_NEGASIT = "43217659"
CNP = "1900101400012"

#: tastează în câmpul `name` al formularului, ca un client (evenimentul `input` pornește căutarea)
TYPE_JS = """
const type = (name, value) => {
    const input = document.querySelector(`[name="${name}"]`);
    input.value = value;
    input.dispatchEvent(new Event("input", {bubbles: true}));
    input.dispatchEvent(new Event("change", {bubbles: true}));
};
const pause = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
// the interaction starts after the page is loaded: before that, typing looks up nothing
const ready = async () => {
    while (!document.querySelector(".o_anaf_feedback")) {
        await pause(100);
    }
};
const save = () => [...document.getElementsByName("website_sale_main_button")].find((b) => b.offsetParent).click();
"""

#: căutarea are o întârziere de 700 ms după ultima tastă, apoi cererea către server
LOOKUP_WAIT = 2500

#: formularul se vede în întregime, cu câmpurile firmei și mesajul ANAF
FORM = "form.address_autoformat"


def _typing(*steps):
    """JS async: tastează pașii dați (``(câmp, valoare)``) și așteaptă răspunsul ANAF."""
    body = "\n".join(f"type({json.dumps(name)}, {json.dumps(value)});" for name, value in steps)
    return f"async () => {{ {TYPE_JS} await ready(); {body} await pause({LOOKUP_WAIT}); }}"


@tagged("-at_install", "post_install", "fise_screenshots")
class TestWebsiteAnafScreenshots(ScreenshotCase or object):
    screenshots_module = "l10n_ro_website_anaf"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="RO Company")
        env = cls.env
        romanian = env["res.lang"]._activate_lang("ro_RO")
        website = env["website"].get_current_website()
        website.language_ids |= romanian
        website.default_lang_id = romanian
        cls.website = website
        cls.ro = env.ref("base.ro")
        states = env["res.country.state"].search([("country_id", "=", cls.ro.id)])
        cls.state_cj = states.filtered(lambda s: s.code == "CJ")[:1]
        cls.state_is = states.filtered(lambda s: s.code == "IS")[:1]

        cls.buyer = new_test_user(env, login="client_magazin", groups="base.group_portal", name="Ion Popescu")
        cls.buyer.lang = "ro_RO"
        cls.buyer.partner_id.write(
            {
                "country_id": cls.ro.id,
                "email": "ion.popescu@example.com",
                "phone": "+40 722 123 456",
                "lang": "ro_RO",
            }
        )
        tax = env["account.tax"].search(
            [("type_tax_use", "=", "sale"), ("amount", "=", 21), ("company_id", "=", env.company.id)], limit=1
        )
        cls.product = env["product.product"].create(
            {
                "name": "Raft metalic 5 polițe",
                "list_price": 450,
                "sale_ok": True,
                "is_published": True,
                "taxes_id": [(6, 0, tax.ids)],
            }
        )
        cls.cart = env["sale.order"].create(
            {
                "partner_id": cls.buyer.partner_id.id,
                "website_id": website.id,
                "order_line": [(0, 0, {"product_id": cls.product.id, "product_uom_qty": 2})],
            }
        )
        cls.answers = {
            CUI_ACTIVA: cls._company("ALFA DISTRIBUȚIE SRL", "Str. Memorandumului Nr. 28", "Cluj-Napoca", "400114"),
            CUI_INACTIVA: cls._company(
                "BETA CONSTRUCT SRL",
                "Bd. Independenței Nr. 12",
                "Iași",
                "700100",
                state=cls.state_is,
                anaf_inactive=True,
                anaf_inactive_date="2026-03-15",
                # firma inactivă are codul de TVA anulat: nu mai este plătitoare de TVA
                l10n_ro_vat_subjected=False,
            ),
            CUI_RADIATA: cls._company(
                "GAMA COMERȚ SRL", "Str. Horea Nr. 5", "Cluj-Napoca", "400174", anaf_radiated=True
            ),
        }

    @classmethod
    def _company(cls, name, street, city, zip_code, state=None, **values):
        return (
            "found",
            {
                "name": name,
                "street": street,
                "city": city,
                "zip": zip_code,
                "nrc": "J12/1234/2015",
                # pe 19.0 `anaf.anaf_lookup` întoarce și tipul: controllerul bifează „este firmă” din el
                "company_type": "company",
                "state_id": state or cls.state_cj,
                "l10n_ro_vat_subjected": True,
                "anaf_inactive": False,
                "anaf_inactive_date": "",
                "anaf_radiated": False,
                **values,
            },
        )

    def _fake_anaf(self, env, number):
        return self.answers.get(number, ("not_found", {}))

    def setUp(self):
        super().setUp()
        main._cache.clear()
        main._hits.clear()
        self.patcher = patch.object(anaf, "anaf_lookup", side_effect=self._fake_anaf)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def _address_shot(self, name, script=None, highlight=None, **extra):
        shot = {
            "path": f"/shop/address?partner_id={self.buyer.partner_id.id}&address_type=billing",
            "name": name,
            "wait": "input[name='vat'][data-anaf-lookup]",
            "full": True,
            "settle": 1500,
        }
        if script:
            shot.update(eval=script, eval_wait=800)
        if highlight:
            shot["highlight"] = highlight
        shot.update(extra)
        return shot

    def _capture_shop(self, shots):
        """Capturile din magazin, ca clientul portal (sesiunea lui are coșul)."""
        # capture_screenshots autentifică din nou utilizatorul: coșul se pune pe sesiunea nouă
        original = self.authenticate

        def authenticate(login, password, **kwargs):
            session = original(login, password, **kwargs)
            self.session["sale_order_id"] = self.cart.id
            odoo.http.root.session_store.save(self.session)
            return session

        with patch.object(self, "authenticate", side_effect=authenticate):
            return self.capture_screenshots(shots, login="client_magazin", viewport=(1440, 1100), hide_systray=True)

    def test_capture_fise(self):
        # câmpurile se evidențiază prin div-ul lor (cu eticheta): un <input> nu poate purta bulina numerotată
        company_fields = ["#company_name_div", "#div_street", "#div_city", "#div_zip:visible", "#div_state"]
        save_button = "[name='website_sale_main_button']:visible"
        self._capture_shop(
            [
                # 1. Formularul de adresă de facturare, înainte de codul fiscal.
                self._address_shot(
                    "01_formular_adresa.png",
                    highlight=["#div_vat", "#company_name_div"],
                ),
                # 2. Codul fiscal tastat: firma găsită la ANAF și câmpurile goale completate.
                self._address_shot(
                    "02_firma_gasita.png",
                    _typing(("vat", f"RO{CUI_ACTIVA}")),
                    highlight=["#div_vat", *company_fields],
                ),
                # 3. Strada tastată de client rămâne; butonul „Completează din ANAF" e la vedere.
                self._address_shot(
                    "03_strada_tastata.png",
                    _typing(("street", "Depozit, Str. Fabricii Nr. 3"), ("vat", CUI_ACTIVA)),
                    highlight=["#div_street", ".o_anaf_fill"],
                ),
                # 4. După „Completează din ANAF": adresa vine de la ANAF.
                self._address_shot(
                    "04_completat_din_anaf.png",
                    f"async () => {{ {TYPE_JS} await ready(); type('street', 'Depozit, Str. Fabricii Nr. 3'); "
                    f"type('vat', '{CUI_ACTIVA}'); await pause({LOOKUP_WAIT}); "
                    "document.querySelector('.o_anaf_fill').click(); await pause(300); }",
                    highlight=["#div_street"],
                ),
                # 5. Firmă inactivă fiscal: avertisment, comanda se poate plasa.
                self._address_shot(
                    "05_firma_inactiva.png",
                    _typing(("vat", f"RO{CUI_INACTIVA}")),
                    highlight=["#div_vat", save_button],
                ),
                # 6. Firmă radiată: nu poate comanda.
                self._address_shot(
                    "06_firma_radiata.png",
                    _typing(("vat", CUI_RADIATA)),
                    highlight=["#div_vat"],
                ),
                # 7. Cod fiscal care nu apare la ANAF.
                self._address_shot(
                    "07_cod_negasit.png",
                    _typing(("vat", CUI_NEGASIT)),
                    highlight=["#div_vat"],
                ),
                # 8. CNP tastat din greșeală.
                self._address_shot(
                    "08_cnp.png",
                    _typing(("vat", CNP)),
                    highlight=["#div_vat"],
                ),
                # 9. La salvare, firma radiată este refuzată (verificarea de pe server).
                self._address_shot(
                    "09_refuz_la_salvare.png",
                    f"async () => {{ {TYPE_JS} await ready(); type('vat', '{CUI_RADIATA}'); await pause({LOOKUP_WAIT}); "
                    "type('street', 'Str. Horea Nr. 5'); type('city', 'Cluj-Napoca'); type('zip', '400174'); "
                    f"const st = document.querySelector('[name=state_id]'); st.value = '{self.state_cj.id}'; "
                    "st.dispatchEvent(new Event('change', {bubbles: true})); "
                    "save(); await pause(2500); }",
                    highlight=["#errors", "#div_vat"],
                ),
            ]
        )

        # 10. Firma inactivă salvată: coșul merge mai departe; pe 19.0 partenerul clientului devine firma.
        self._capture_shop(
            [
                {
                    **self._address_shot(
                        "10_adresa_salvata.png",
                        f"async () => {{ {TYPE_JS} await ready(); type('vat', 'RO{CUI_INACTIVA}'); await pause({LOOKUP_WAIT}); "
                        "save(); }",
                    ),
                    "eval_wait": 4000,
                    "settle": 2000,
                },
            ]
        )
        self.env.invalidate_all()
        # pe 19.0 denumirea legală se scrie pe partenerul clientului, care devine firmă (fără firmă-părinte)
        company = self.buyer.partner_id
        self.assertEqual(company.name, "BETA CONSTRUCT SRL", "denumirea legală merge pe partenerul clientului")
        self.assertTrue(company.is_company, "partenerul clientului devine firmă")
        self.assertFalse(company.parent_id, "nu se creează o firmă-părinte")
        note = self.cart.message_ids.filtered(lambda m: "inactive" in (m.body or "") or "inactiv" in (m.body or ""))
        self.assertTrue(note, "coșul primește nota pentru firma inactivă")

        # 11–12. În backend: comanda cu nota internă și partenerul devenit firmă din ANAF.
        orders = self.env.ref("sale.action_quotations_with_onboarding")
        contacts = self.env.ref("contacts.action_contacts", raise_if_not_found=False) or self.env.ref(
            "base.action_partner_form"
        )
        self.capture_screenshots(
            [
                {
                    "url": f"action={orders.id}&id={self.cart.id}&model=sale.order&view_type=form",
                    "name": "11_comanda_nota_inactiva.png",
                    "wait": ".o_form_view",
                    "hide_chatter": False,
                    "highlight": [
                        "label.o_form_label[for^='partner_id']",
                        ".o-mail-Message-body:has-text('ANAF')",
                    ],
                    "settle": 2500,
                },
                {
                    "url": f"action={contacts.id}&id={company.id}&model=res.partner&view_type=form",
                    "name": "12_firma_din_anaf.png",
                    "wait": ".o_form_view",
                    "highlight": [
                        "div[name='name']",
                        "label.o_form_label[for^='vat']",
                        "div[name='company_type'] .o_radio_item:has-text('Companie')",
                    ],
                    "settle": 2000,
                },
            ],
            viewport=(1600, 1000),
        )
