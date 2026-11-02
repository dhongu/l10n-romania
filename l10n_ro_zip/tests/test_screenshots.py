# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Coduri poștale pe stradă” (readme/FISA_CONSULTANT.md, în RO, în
# readme/screenshots/) și pentru readme/USAGE.md (în EN, în readme/screenshots/en/).
#
# Nomenclatorul vine din data/res_zip.sql, deci capturile arată înregistrări reale ale Poștei
# Române; partenerul este de exemplu. Căutarea în câmpul „Cod poștal” se face tastând în
# browser, ca operatorul.
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_zip,deltatech_doc_screenshots \
#       --test-tags=/l10n_ro_zip:TestResZipScreenshots --stop-after-init
import os
import unittest

from odoo.modules.module import get_module_path
from odoo.tests import tagged

try:
    from odoo.addons.deltatech_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    try:
        from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
    except ImportError:
        ScreenshotCase = None

# bulinele numerotate stau la stânga câmpului, ca să nu acopere prima literă a valorii
BADGES_LEFT = """
    const style = document.createElement("style");
    style.textContent = ".o_form_view [data-fise-badge] { left: -30px !important; }";
    document.head.appendChild(style);
"""

# caută în listă după începutul codului poștal (Iași, 7001..)
SEARCH_CODE = """
async () => {
    const input = document.querySelector(".o_searchview_input");
    input.focus();
    input.value = "70011";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    await new Promise((resolve) => setTimeout(resolve, 800));
    input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    await new Promise((resolve) => setTimeout(resolve, 2000));
}
"""

# tastează în câmpul „Cod poștal” al partenerului și așteaptă lista de propuneri
TYPE_STREET = (
    """
async () => {
"""
    + BADGES_LEFT
    + """
    const input = document.querySelector("div[name='zip_id'] input");
    input.focus();
    input.value = "Nicolae Balcescu";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    for (let i = 0; i < 50 && !document.querySelector(".o-autocomplete--dropdown-item"); i++) {
        await new Promise((resolve) => setTimeout(resolve, 200));
    }
}
"""
)

# aceeași căutare, apoi alegerea primei propuneri (Strada Balcescu Nicolae, 700117)
PICK_STREET = (
    TYPE_STREET.rstrip().rstrip("}")
    + """
    document.querySelector(".o-autocomplete--dropdown-item a, .o-autocomplete--dropdown-item").click();
    await new Promise((resolve) => setTimeout(resolve, 1500));
}
"""
)

ADDRESS = [
    "div[name='city_id']",
    "div[name='state_id']",
    "div[name='zip']",
    "div[name='zip_id']",
]


@tagged("-at_install", "post_install", "fise_screenshots")
class TestResZipScreenshots(ScreenshotCase or object):
    screenshots_module = "l10n_ro_zip"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("deltatech_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="RO Company")
        env = cls.env
        ro = env.ref("base.ro")
        iasi = env["res.city"].search(
            [("country_id", "=", ro.id), ("state_id.code", "=", "IS"), ("name", "=", "Iași")], limit=1
        )
        cls.zip_bucharest = env["res.zip"].search(
            [("name", "=", "011376"), ("street_name", "=", "1 Mai"), ("sector", "=", "1")], limit=1
        )
        assert iasi and cls.zip_bucharest, "nomenclatorul de coduri poștale nu e încărcat"
        cls.partner = env["res.partner"].create(
            {
                "name": "Exemplu Distribuție SRL",
                "is_company": True,
                "country_id": ro.id,
                "state_id": iasi.state_id.id,
                "city_id": iasi.id,
                "city": iasi.name,
                "street": "Strada Nicolae Bălcescu nr. 12",
                "lang": "ro_RO",
            }
        )
        cls.action = env.ref("l10n_ro_zip.action_res_zip")
        cls.menu = env.ref("contacts.menu_contacts")
        env.flush_all()

    def screenshots_dir(self, lang="ro_RO"):
        # capturile EN ale USAGE.md stau tot sub readme/screenshots/, lângă cele RO
        if lang != "ro_RO":
            return os.path.join(get_module_path(self.screenshots_module), "readme", "screenshots", lang.split("_")[0])
        return super().screenshots_dir(lang)

    def _shots(self):
        partner_url = f"id={self.partner.id}&model=res.partner&view_type=form&menu_id={self.menu.id}"
        return [
            {
                "url": f"action={self.action.id}&view_type=list&menu_id={self.menu.id}",
                "name": "01_lista_coduri_postale.png",
                "wait": ".o_list_view .o_data_row",
                "eval": SEARCH_CODE,
                "eval_wait": 1000,
                "highlight": ".o_searchview",
            },
            {
                "url": f"action={self.action.id}&id={self.zip_bucharest.id}&model=res.zip&view_type=form"
                f"&menu_id={self.menu.id}",
                "name": "02_fisa_cod_postal.png",
                "wait": ".o_form_view",
            },
            {
                "url": partner_url,
                "name": "03_partener_cautare_strada.png",
                "wait": ".o_form_view div[name='zip_id'] input",
                "eval": TYPE_STREET,
                "eval_wait": 1000,
                "highlight": ["div[name='city_id']", "div[name='zip_id']"],
                "settle": 1500,
            },
            {
                "url": partner_url,
                "name": "04_partener_cod_completat.png",
                "wait": ".o_form_view div[name='zip_id'] input",
                "eval": PICK_STREET,
                "eval_wait": 1000,
                "highlight": ADDRESS,
                "settle": 1500,
            },
        ]

    def test_capture_fise(self):
        self.capture_screenshots(self._shots())

    def test_capture_usage(self):
        self.capture_screenshots(self._shots(), lang="en_US")
