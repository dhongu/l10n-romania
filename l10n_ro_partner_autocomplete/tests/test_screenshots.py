# © 2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Completarea partenerilor din ANAF", în RO, pe planul RO.
# Serviciile ANAF și VIES sunt simulate (patch pe `l10n.ro.anaf.partner.lookup._request` și
# `_vies_request`), la fel verificarea VIES standard a `base_vat` (prin IAP), deci capturile nu depind
# de rețea și nu consumă credite IAP: răspunsurile sunt în forma reală a serviciilor ANAF v9 și VIES.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -u l10n_ro_partner_autocomplete \
#       --test-tags=fise_screenshots/l10n_ro_partner_autocomplete --stop-after-init
import unittest
from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ro_anaf_partner_lookup.tests.test_anaf_partner_lookup import CUI, REQUEST_PATH, anaf_result
from odoo.addons.l10n_ro_anaf_partner_lookup.tests.test_vies_lookup import VIES_PATH, VIES_VAT, vies_answer

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None

#: firmele cunoscute de ANAF-ul simulat, câte una pentru fiecare pas, ca să nu apară ca duplicate
CUI_INVOICE = "24686420"
CUI_REFRESH = "15975313"

#: CUI → (denumire, NRC, telefon, stradă, număr, cod poștal)
COMPANIES = {
    CUI_INVOICE: ("LOGISTIC TRANS VEST S.R.L.", "J35/880/2015", "0256300400", "Calea Aradului", "40", "300088"),
    CUI_REFRESH: ("MOBILA DESIGN BANAT S.R.L.", "J35/2210/2009", "0256400500", "Str. Gheorghe Lazăr", "24", "300081"),
}


def _anaf_answer(cui, timeout=None):
    """Răspunsul simulat al ANAF, în forma serviciului v9; ``{}`` (negăsit) pentru alt CUI"""
    if cui == CUI:
        return anaf_result()
    if cui not in COMPANIES:
        return {}
    name, nrc, phone, street, number, zip_code = COMPANIES[cui]
    answer = anaf_result(cui=int(cui), denumire=name, nrRegCom=nrc, telefon=phone, codPostal=zip_code)
    answer["adresa_domiciliu_fiscal"] = {
        "ddenumire_Strada": street,
        "dnumar_Strada": number,
        "ddenumire_Localitate": "Mun. Timişoara",
        "dcod_JudetAuto": "TM",
        "ddetalii_Adresa": "",
        "dcod_Postal": zip_code,
    }
    return answer


#: verificarea VIES standard a base_vat (prin IAP), la salvarea unui cod de TVA din altă țară UE
BASE_VAT_VIES_PATH = "odoo.addons.base_vat.models.res_partner.ResPartner._check_vies_iap"

#: firma din altă țară UE, introdusă demult, de actualizat din VIES (pasul 10)
VIES_VAT_REFRESH = "HU10773381"
VIES_COMPANIES = {
    VIES_VAT: vies_answer(),
    VIES_VAT_REFRESH: vies_answer(name="DUNA TRADE KFT", address="KONYVES KALMAN KÖRÚT 36 1097 BUDAPEST"),
}


def _vies_answer(prefix, number, timeout=None):
    """Răspunsul simulat al VIES: firmele de mai sus și firmele românești plătitoare de TVA ale
    ANAF-ului simulat; orice alt cod e neînregistrat"""
    vat = prefix + number
    if vat in VIES_COMPANIES:
        return VIES_COMPANIES[vat]
    if prefix == "RO" and (number == CUI or number in COMPANIES):
        return vies_answer(name="---", address="---")
    return vies_answer("INVALID", "---", "---")


#: JS care oprește salvarea automată a formularului la plecarea de pe pagină: un CUI doar tastat
#: în nume ar crea, la shot-ul următor, partenerul din ANAF (funcția „partener creat cu CUI ca nume")
#: (salvarea urgentă pleacă prin `navigator.sendBeacon`)
NO_AUTOSAVE = (
    " navigator.sendBeacon = () => true;"
    " window.addEventListener('beforeunload', (e) => e.stopImmediatePropagation(), true);"
    " document.addEventListener('visibilitychange', (e) => e.stopImmediatePropagation(), true);"
)


def _type_js(selector, text, wait=3500, pick=None):
    """JS care tastează ``text`` în câmpul ``selector`` și, opțional, alege sugestia ``pick``"""
    script = (
        "async () => {" + ("" if pick else NO_AUTOSAVE) + f" const input = document.querySelector({selector!r});"
        " input.focus(); input.click();"
        f" input.value = {text!r};"
        " input.dispatchEvent(new InputEvent('input', {bubbles: true}));"
        f" await new Promise(r => setTimeout(r, {wait}));"
    )
    if pick:
        script += (
            f" const option = document.querySelector({pick!r});"
            " if (option) { option.click(); }"
            " await new Promise(r => setTimeout(r, 2500));"
        )
    return script + " }"


@tagged("-at_install", "post_install", "fise_screenshots")
class TestPartnerAutocompleteScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_partner_autocomplete"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        company = cls.prepare_ro_company(name="Demo Parteneri ANAF SRL")
        env = cls.env
        cls.admin = env.ref("base.user_admin")
        cls.admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        Partner = env["res.partner"].with_context(l10n_ro_anaf_no_autofill=True)

        # Pașii 6–7: o firmă introdusă demult, cu numele și adresa vechi; telefonul local se păstrează
        cls.old_partner = Partner.create(
            {
                "name": "Mobila Design Banat",
                "is_company": True,
                "vat": "RO" + CUI_REFRESH,
                "country_id": env.ref("base.ro").id,
                "state_id": env.ref("base.RO_TM").id,
                "city": "Timișoara",
                "street": "Str. Mercy Nr. 2",
                "zip": "300041",
                "phone": "0722 111 222",
                "customer_rank": 1,
            }
        )
        # Pasul 10: o firmă din Ungaria, cu adresa veche; „Valabil în comunitate" se vede doar cu
        # verificarea VIES pornită pe companie (setarea standard din Contabilitate)
        with patch(BASE_VAT_VIES_PATH, return_value="invalid"):
            company.vat_check_vies = True
            cls.eu_partner = Partner.create(
                {
                    "name": "Duna Trade",
                    "is_company": True,
                    "vat": VIES_VAT_REFRESH,
                    "country_id": env.ref("base.hu").id,
                    "city": "Budapesta",
                    "street": "Váci út 1",
                    "zip": "1062",
                    "supplier_rank": 1,
                }
            )
            # vies_valid (calculat, stocat) se calculează la flush: tot sub patch
            env.flush_all()

    def _anaf(self):
        return patch(REQUEST_PATH, side_effect=_anaf_answer)

    def _vies(self):
        return patch(VIES_PATH, side_effect=_vies_answer)

    def _base_vat_vies(self):
        return patch(BASE_VAT_VIES_PATH, return_value="invalid")

    def test_capture_fise(self):
        settings = self.env.ref("base_setup.action_general_configuration")
        customers = self.env.ref("account.res_partner_action_customer")
        invoices = self.env.ref("account.action_move_out_invoice_type")
        new_partner = f"action={customers.id}&model=res.partner&view_type=form"
        old_partner = f"action={customers.id}&id={self.old_partner.id}&model=res.partner&view_type=form"
        name_input = "div[name='name'] input"
        vat_input = "div[name='vat'] input"
        suggestion = ".partner_autocomplete_dropdown_char"
        refresh = "button[name='action_l10n_ro_anaf_refresh']"
        vies_refresh = "button[name='action_l10n_ro_vies_refresh']"
        vendors = self.env.ref("account.res_partner_action_supplier")
        eu_partner = f"action={vendors.id}&id={self.eu_partner.id}&model=res.partner&view_type=form"
        with self._anaf(), self._vies(), self._base_vat_vies():
            self.capture_screenshots(
                [
                    # 1. Setări generale: nota sub „Partner Autocomplete"
                    {
                        "url": f"action={settings.id}",
                        "name": "01_setari_autocomplete.png",
                        "wait": "#partner_autocomplete",
                        "timeout": 60000,
                        "eval": "() => document.querySelector('#partner_autocomplete')"
                        ".scrollIntoView({block: 'center'})",
                        "highlight": ["#partner_autocomplete"],
                        "settle": 2000,
                    },
                    # 2. Partener nou: CUI tastat în nume, sugestia vine de la ANAF
                    {
                        "url": new_partner,
                        "name": "02_sugestie_cui_nume.png",
                        "wait": name_input,
                        "eval": _type_js(name_input, CUI),
                        "eval_wait": 500,
                        "highlight": [name_input, suggestion],
                        "settle": 1500,
                    },
                    # 3. Sugestia aleasă: formularul completat și salvat, cu nota ANAF în istoric
                    {
                        "url": new_partner,
                        "name": "03_partener_completat.png",
                        "wait": name_input,
                        "eval": _type_js(name_input, CUI, pick=suggestion),
                        "eval_wait": 1500,
                        "hide_chatter": False,
                        "highlight": [
                            "div[name='company_type']",
                            "div[name='name']",
                            ".o_address_format",
                            "div[name='vat']",
                            "div[name='l10n_ro_vat_subjected']",
                            ".o-mail-Message:has-text('ANAF')",
                        ],
                        "settle": 2000,
                    },
                    # 4. Partener nou: CUI tastat fără RO în câmpul TVA
                    {
                        "url": new_partner,
                        "name": "04_sugestie_cui_tva.png",
                        "wait": vat_input,
                        "eval": _type_js(vat_input, CUI_INVOICE),
                        "eval_wait": 500,
                        "highlight": [vat_input, suggestion],
                        "settle": 1500,
                    },
                    # 5. Factura nouă: CUI tastat la Client
                    {
                        "url": f"action={invoices.id}&model=account.move&view_type=form",
                        "name": "05_sugestie_client_factura.png",
                        "wait": "div[name='partner_id'] input",
                        "eval": _type_js("div[name='partner_id'] input", "RO" + CUI_INVOICE),
                        "eval_wait": 500,
                        "highlight": ["div[name='partner_id']", ".partner_autocomplete_dropdown_many2one"],
                        "settle": 1500,
                    },
                    # 6. Firmă existentă: butonul „Actualizează din ANAF" (iconița) lângă codul fiscal
                    {
                        "url": old_partner,
                        "name": "06_buton_actualizare_anaf.png",
                        "wait": refresh,
                        "highlight": [".o_address_format", refresh, "div[name='l10n_ro_vat_subjected']"],
                        "settle": 1500,
                    },
                    # 7. După actualizare: datele noi și lista modificărilor în istoric
                    {
                        "url": old_partner,
                        "name": "07_actualizare_istoric.png",
                        "wait": refresh,
                        "click_btn": refresh,
                        "wait_after": ".o-mail-Message:has-text('ANAF')",
                        "hide_chatter": False,
                        "highlight": [
                            ".o_address_format",
                            "div[name='l10n_ro_vat_subjected']",
                            ".o-mail-Message:has-text('ANAF')",
                        ],
                        "settle": 2500,
                    },
                    # 8. Partener nou: codul de TVA al unei firme din Italia, tastat în TVA
                    {
                        "url": new_partner,
                        "name": "08_sugestie_vies.png",
                        "wait": vat_input,
                        "eval": _type_js(vat_input, VIES_VAT),
                        "eval_wait": 500,
                        "highlight": [vat_input, suggestion],
                        "settle": 1500,
                    },
                    # 9. Sugestia VIES aleasă din nume: firma completată, „Valabil în comunitate", nota VIES
                    {
                        "url": new_partner,
                        "name": "09_partener_ue_completat.png",
                        "wait": name_input,
                        "eval": _type_js(name_input, VIES_VAT, pick=suggestion),
                        "eval_wait": 1500,
                        "hide_chatter": False,
                        "highlight": [
                            "div[name='name']",
                            ".o_address_format",
                            "div[name='vat']",
                            "div[name='vies_valid']",
                            ".o-mail-Message:has-text('preluate din VIES')",
                        ],
                        "settle": 2000,
                    },
                    # 10. Firmă UE existentă: „Actualizează din VIES", adresa nouă și nota în istoric
                    {
                        "url": eu_partner,
                        "name": "10_actualizare_vies.png",
                        "wait": vies_refresh,
                        "click_btn": vies_refresh,
                        "wait_after": ".o-mail-Message:has-text('Actualizat din VIES')",
                        "hide_chatter": False,
                        "highlight": [
                            vies_refresh,
                            ".o_address_format",
                            "div[name='vies_valid']",
                            ".o-mail-Message:has-text('Actualizat din VIES')",
                        ],
                        "settle": 2500,
                    },
                ],
                viewport=(1600, 950),
            )
