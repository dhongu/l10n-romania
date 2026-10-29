# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Căutarea firmei la ANAF după CUI".
#
# Modulul nu are ecran propriu: capturile arată parametrii de sistem opționali și partenerii
# creați din valorile întoarse de `lookup`, cum îi creează modulele care îl folosesc. Răspunsul
# ANAF este simulat, deci rularea nu depinde de serviciul ANAF. Pe 19.0, ID Companie
# (company_registry, calculat de l10n_ro din TVA) stă în tabul „Vânzări & Achiziții”.
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_anaf_partner_lookup,l10n_ro,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_anaf_partner_lookup:TestAnafPartnerLookupScreenshots --stop-after-init
import unittest
from unittest.mock import patch

from odoo.tests import tagged

from .test_anaf_partner_lookup import REQUEST_PATH

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None

# bulina ①/⑤ de la TVA și NRC (coloana a doua) e îngustată de stilul câmpului: o fixăm la
# mărimea ei, cu o regulă CSS (bulinele se adaugă după acest cod)
SHOW_BADGES = """
const style = document.createElement("style");
style.textContent = ".o_form_view [data-fise-badge] { width: 24px !important; min-width: 24px !important;"
    + " max-width: none !important; padding: 0 !important; }";
document.head.appendChild(style);
"""

PARTNER_FIELDS = [
    "div[name='vat']",
    "div[name='street']",
    "div[name='city']",
    "div[name='state_id']",
]


def _answer(cui, name, vat_payer, office, fiscal, trade_register="", phone=""):
    """Un răspuns al serviciului ANAF v9, în forma lui"""
    return {
        "date_generale": {
            "cui": int(cui),
            "denumire": name,
            "nrRegCom": trade_register,
            "telefon": phone,
            "stare_inregistrare": "INREGISTRAT din data 02.10.2012",
        },
        "inregistrare_scop_Tva": {"scpTVA": vat_payer},
        "stare_inactiv": {"statusInactivi": False, "dataRadiere": ""},
        "adresa_sediu_social": {f"s{key}": value for key, value in office.items()},
        "adresa_domiciliu_fiscal": {f"d{key}": value for key, value in fiscal.items()},
    }


@tagged("-at_install", "post_install", "fise_screenshots")
class TestAnafPartnerLookupScreenshots(ScreenshotCase or object):
    screenshots_module = "l10n_ro_anaf_partner_lookup"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        company = cls.prepare_ro_company(name="RO Company")
        env = cls.env
        if "product.pricelist" in env:
            # lista de prețuri implicită a bazei fără demo rămâne în USD: în RON, ca pe firmă
            env["product.pricelist"].search([]).currency_id = company.currency_id
        params = env["ir.config_parameter"].sudo()
        params.set_param("l10n_ro_anaf_partner_lookup.url", "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva")
        params.set_param("l10n_ro_anaf_partner_lookup.timeout", "10")
        cls.params_action = env["ir.actions.act_window"].create(
            {
                "name": "Parametri sistem",
                "res_model": "ir.config_parameter",
                "view_mode": "list,form",
                "domain": [("key", "=like", "l10n_ro_anaf_partner_lookup.%")],
            }
        )

        lookup = env["l10n.ro.anaf.partner.lookup"]
        # Firmă plătitoare de TVA, cu sediul social și domiciliul fiscal în localități diferite:
        # adresa vine întreagă din sediul social
        office_answer = _answer(
            "12345674",
            "EXEMPLU DISTRIBUŢIE S.R.L.",
            True,
            office={
                "denumire_Strada": "Str. Ciprian Porumbescu",
                "numar_Strada": "12",
                "detalii_Adresa": "Etaj 1",
                "denumire_Localitate": "Mun. Timişoara",
                "cod_JudetAuto": "TM",
                "cod_Postal": "300045",
            },
            fiscal={
                "denumire_Strada": "Bd. Revoluţiei",
                "numar_Strada": "5",
                "denumire_Localitate": "Mun. Arad",
                "cod_JudetAuto": "AR",
                "cod_Postal": "310025",
            },
            trade_register="J35/1234/2012",
            phone="0256123456",
        )
        # Firmă neplătitoare de TVA din București: adresa scrisă cu majuscule, sectorul lipsă
        # din localitate și codul poștal fără 0-ul din față
        bucharest_answer = _answer(
            "45678900",
            "ATELIER EXEMPLU S.R.L.",
            False,
            office={
                "denumire_Strada": "STR. MĂRĂŞEŞTI",
                "numar_Strada": "7",
                "denumire_Localitate": "Mun. Bucureşti",
                "cod_JudetAuto": "B",
                "cod_Postal": "30167",
            },
            fiscal={},
            trade_register="J40/5678/2019",
        )
        with patch(REQUEST_PATH, return_value=office_answer):
            cls.office_result = lookup.lookup("RO 12345674")
        with patch(REQUEST_PATH, return_value=bucharest_answer):
            cls.bucharest_result = lookup.lookup("45678900")
        assert cls.office_result["state"] == "found" and cls.bucharest_result["state"] == "found"
        # limba nu vine de la ANAF: o fixăm doar ca formularul să nu arate „English (US)"
        lang = {"lang": "ro_RO"} if env["res.lang"].search_count([("code", "=", "ro_RO")]) else {}
        cls.office_partner = env["res.partner"].create({**cls.office_result["partner"], **lang})
        cls.bucharest_partner = env["res.partner"].create({**cls.bucharest_result["partner"], **lang})
        env.flush_all()

    def test_capture_fise(self):
        nrc = ["div[name='nrc']"] if "nrc" in self.env["res.partner"]._fields else []
        self.capture_screenshots(
            [
                {
                    "url": f"action={self.params_action.id}&view_type=list",
                    "name": "01_parametri_sistem.png",
                    "wait": ".o_list_view .o_data_row",
                },
                {
                    "url": f"id={self.office_partner.id}&model=res.partner&view_type=form",
                    "name": "02_firma_platitoare_tva.png",
                    "wait": ".o_form_view",
                    "highlight": PARTNER_FIELDS + nrc + ["div[name='zip']"],
                    "eval": SHOW_BADGES,
                    "settle": 2000,
                },
                {
                    "url": f"id={self.bucharest_partner.id}&model=res.partner&view_type=form",
                    "name": "03_firma_bucuresti_sector.png",
                    "wait": ".o_form_view",
                    "highlight": PARTNER_FIELDS + ["div[name='zip']"],
                    "eval": SHOW_BADGES,
                    "settle": 2000,
                },
                {
                    # ID Companie (CUI-ul fără RO) e în tabul „Vânzări & Achiziții”, grupul Diverse
                    "url": f"id={self.office_partner.id}&model=res.partner&view_type=form",
                    "name": "04_id_companie.png",
                    "wait": ".o_form_view",
                    "click_tab": "Vânzări & Achiziții",
                    "highlight": ["div[name='vat']", "div[name='company_registry']"],
                    "eval": SHOW_BADGES,
                    "settle": 2000,
                },
            ]
        )
