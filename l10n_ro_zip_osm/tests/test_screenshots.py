# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi de ecran pentru fișa „Străzile orașelor mici” (readme/FISA_CONSULTANT.md, în RO, în
# static/description/) și pentru readme/USAGE.md (în EN, în static/description/en/).
#
# Străzile vin din data/res_zip_osm.sql (OpenStreetMap), deci capturile arată rânduri reale;
# partenerul este de exemplu. Orașul ales este Huși (cod poștal unic 735100).
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_zip_osm,deltatech_doc_screenshots \
#       --test-tags=/l10n_ro_zip_osm:TestZipOsmScreenshots --stop-after-init
import unittest

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

# caută în listă codul poștal unic al orașului Huși
SEARCH_CODE = """
async () => {
    const input = document.querySelector(".o_searchview_input");
    input.focus();
    input.value = "735100";
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
    input.value = "Stefan cel Mare";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    for (let i = 0; i < 50 && !document.querySelector(".o-autocomplete--dropdown-item"); i++) {
        await new Promise((resolve) => setTimeout(resolve, 200));
    }
}
"""
)

# aceeași căutare, apoi alegerea primei propuneri (Strada Stefan cel Mare, 735100)
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
class TestZipOsmScreenshots(ScreenshotCase or object):
    screenshots_module = "l10n_ro_zip_osm"

    @classmethod
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("deltatech_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="RO Company")
        env = cls.env
        ro = env.ref("base.ro")
        husi = env["res.city"].search(
            [("country_id", "=", ro.id), ("state_id.code", "=", "VS"), ("zipcode", "=", "735100")], limit=1
        )
        assert husi, "localitatea Huși (l10n_ro_city) nu e încărcată"
        cls.partner = env["res.partner"].create(
            {
                "name": "Exemplu Distribuție SRL",
                "is_company": True,
                "country_id": ro.id,
                "state_id": husi.state_id.id,
                "city_id": husi.id,
                "city": husi.name,
                # la alegerea localității, Odoo pune deja codul ei în adresă
                "zip": husi.zipcode,
                "street": "Strada Ștefan cel Mare nr. 5",
                "lang": "ro_RO",
            }
        )
        cls.action = env.ref("l10n_ro_zip.action_res_zip")
        cls.menu = env.ref("contacts.menu_contacts")
        env.flush_all()

    def _shots(self):
        partner_url = f"id={self.partner.id}&model=res.partner&view_type=form&menu_id={self.menu.id}"
        return [
            {
                "url": f"action={self.action.id}&view_type=list&menu_id={self.menu.id}",
                "name": "01_lista_strazi_oras_mic.png",
                "wait": ".o_list_view .o_data_row",
                "eval": SEARCH_CODE,
                "eval_wait": 1000,
                "highlight": ".o_searchview",
            },
            {
                "url": partner_url,
                "name": "02_partener_cautare_strada.png",
                "wait": ".o_form_view div[name='zip_id'] input",
                "eval": TYPE_STREET,
                "eval_wait": 1000,
                "highlight": ["div[name='city_id']", "div[name='zip_id']"],
                "settle": 1500,
            },
            {
                "url": partner_url,
                "name": "03_partener_cod_completat.png",
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
