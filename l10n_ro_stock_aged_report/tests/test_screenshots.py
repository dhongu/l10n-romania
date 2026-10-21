# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Raportul de vechime a stocului".
#
# Seedează: un depozit cu două sublocații de raft, două categorii (mărfuri pe 371,
# materii prime pe 301) și cuante cu ultima intrare la vârste diferite (de la câteva zile
# la peste un an), unele cu ieșiri recente și altele fără nicio ieșire; apoi calculează
# raportul pe intervale de 30 de zile.
#
# Rulare — RESTRÂNSĂ LA CLASĂ, altfel se rescriu capturile tuturor modulelor cu test de fișe:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_stock_aged_report,l10n_ro_doc_screenshots \
#       --test-tags=/l10n_ro_stock_aged_report:TestStockAgeReportScreenshots --stop-after-init
import unittest
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestStockAgeReportScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_aged_report"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Materiale Construcții Demo SRL")
        env = cls.env
        company = env.company
        admin = env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        for xmlid in (
            "stock.group_stock_user",
            "stock.group_stock_manager",
            "stock.group_stock_multi_locations",
            "uom.group_uom",
        ):
            grp = env.ref(xmlid, raise_if_not_found=False)
            if grp:
                admin.group_ids = [(4, grp.id)]

        cls.warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        if not cls.warehouse:
            cls.warehouse = env["stock.warehouse"].create(
                {"name": "Depozit Central", "code": "DC", "company_id": company.id}
            )
        cls.warehouse.write({"name": "Depozit Central", "code": "DC"})
        # pe panoul Inventar din spatele meniului (captura 1), în loc de „Receipts" / „Delivery Orders"
        cls.warehouse.in_type_id.name = "Recepții"
        cls.warehouse.out_type_id.name = "Livrări"
        cls.stock_location = cls.warehouse.lot_stock_id
        Location = env["stock.location"]
        cls.raft_a = Location.create(
            {"name": "Raft A", "usage": "internal", "location_id": cls.stock_location.id, "company_id": company.id}
        )
        cls.raft_b = Location.create(
            {"name": "Raft B", "usage": "internal", "location_id": cls.stock_location.id, "company_id": company.id}
        )

        Account = env["account.account"].with_company(company)
        acc_371 = Account.search([("code", "=like", "371%")], limit=1)
        acc_301 = Account.search([("code", "=like", "301%")], limit=1)
        cls.categ_marfuri = env["product.category"].create(
            {"name": "Mărfuri", "property_stock_valuation_account_id": acc_371.id}
        )
        cls.categ_materii = env["product.category"].create(
            {"name": "Materii prime", "property_stock_valuation_account_id": acc_301.id}
        )

        uom_unit = env.ref("uom.product_uom_unit")
        uom_kg = env.ref("uom.product_uom_kgm")
        now = fields.Datetime.now()

        def product(name, code, categ, price, uom=uom_unit):
            return env["product.product"].create(
                {
                    "name": name,
                    "default_code": code,
                    "is_storable": True,
                    "categ_id": categ.id,
                    "uom_id": uom.id,
                    "standard_price": price,
                }
            )

        def stock(prod, location, qty, age_in, age_out=None):
            env["stock.quant"]._update_available_quantity(prod, location, qty)
            quant = env["stock.quant"].search([("product_id", "=", prod.id), ("location_id", "=", location.id)])
            # datele se forțează după actualizare: altfel ar rămâne data de azi
            quant.write(
                {
                    "l10n_ro_last_in_date": now - timedelta(days=age_in),
                    "l10n_ro_last_out_date": now - timedelta(days=age_out) if age_out is not None else False,
                }
            )

        ciment = product("Ciment Portland 40 kg", "CIM40", cls.categ_marfuri, 32.50)
        bca = product("BCA 600×250×200 mm", "BCA25", cls.categ_marfuri, 11.80)
        adeziv = product("Adeziv gresie 25 kg", "ADZ25", cls.categ_marfuri, 41.00)
        glet = product("Glet de finisaj 20 kg", "GLT20", cls.categ_marfuri, 38.90)
        polistiren = product("Polistiren expandat 10 cm", "EPS10", cls.categ_marfuri, 19.60)
        tigla = product("Țiglă ceramică roșie", "TGL01", cls.categ_marfuri, 4.75)
        vopsea = product("Vopsea lavabilă albă 15 l", "VOP15", cls.categ_marfuri, 129.00)
        nisip = product("Nisip spălat 0-4 mm", "NIS04", cls.categ_materii, 0.18, uom_kg)
        pigment = product("Pigment oxid de fier", "PIG01", cls.categ_materii, 22.40, uom_kg)

        stock(ciment, cls.raft_a, 180, age_in=4, age_out=1)
        stock(bca, cls.raft_a, 640, age_in=21, age_out=3)
        stock(adeziv, cls.raft_b, 95, age_in=47, age_out=9)
        stock(glet, cls.raft_b, 60, age_in=78, age_out=40)
        stock(polistiren, cls.raft_a, 120, age_in=112, age_out=95)
        stock(tigla, cls.raft_b, 2400, age_in=138)
        stock(vopsea, cls.raft_b, 14, age_in=410)
        stock(nisip, cls.stock_location, 8500, age_in=12, age_out=2)
        stock(pigment, cls.stock_location, 45, age_in=260)

        # liniile se creează în limba utilizatorului: altfel intervalele ar ieși „0 - 30 days"
        Report = env["l10n.ro.stock.age.report"].with_context(lang="ro_RO")
        cls.wizard = Report.create({"warehouse_id": cls.warehouse.id, "interval_days": "30"})
        cls.report = Report.create({"warehouse_id": cls.warehouse.id, "interval_days": "30"})
        cls.report.do_compute_report()

    #: regrupează rândurile pivotului: pliază „Total" și îl redeschide pe câmpul dat
    _PIVOT_ROWS_JS = """async () => {
        const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
        let head = document.querySelector('.o_pivot tbody th.o_pivot_header_cell_opened');
        if (head) { head.click(); await sleep(1000); }
        head = document.querySelector('.o_pivot tbody th.o_pivot_header_cell_closed');
        if (!head) { return; }
        head.click(); await sleep(1000);
        const items = [...document.querySelectorAll('.o-dropdown--menu .dropdown-item')];
        const item = items.find((e) => e.textContent.trim() === '%s');
        if (item) { item.click(); await sleep(1500); }
    }"""

    # ------------------------------------------------------------------
    def test_capture_fise(self):
        act_wizard = self.env.ref("l10n_ro_stock_aged_report.action_stock_age_report")
        act_lines = self.env.ref("l10n_ro_stock_aged_report.action_sheet_age_report_line")
        menu_stock = self.env.ref("stock.menu_stock_root")
        lines_url = f"action={act_lines.id}&active_id={self.report.id}"
        self.capture_screenshots(
            [
                # 1. Meniul Raportare din Inventar, cu raportul modulului
                {
                    "url": f"menu_id={menu_stock.id}",
                    "name": "01_meniu_raport.png",
                    "wait": ".o_main_navbar",
                    "click_btn": ".o_menu_sections button:has-text('Raportare')",
                    "wait_after": ".o-dropdown--menu",
                    "highlight": [
                        ".o-dropdown--menu .dropdown-item:has-text('Stock Age Report'),"
                        ".o-dropdown--menu .dropdown-item:has-text('vechime')"
                    ],
                    "settle": 1500,
                },
                # 2. Dialogul raportului: depozit, dată de referință, interval
                {
                    "url": (
                        f"action={act_wizard.id}&id={self.wizard.id}&model=l10n.ro.stock.age.report&view_type=form"
                    ),
                    "name": "02_wizard.png",
                    "wait": ".modal-content",
                    # fără fundalul gri și lipit de marginea de sus, ca autotrim-ul să
                    # poată tăia zona moartă din jurul dialogului
                    "eval": (
                        "(() => {"
                        " document.querySelectorAll('.modal-backdrop, .o_main_navbar')"
                        "   .forEach(e => e.remove());"
                        " document.querySelectorAll('.modal-dialog').forEach(d => {"
                        "   d.classList.remove('modal-dialog-centered');"
                        "   d.style.margin = '8px auto';"
                        " });"
                        " if (document.activeElement) { document.activeElement.blur(); }"
                        "})()"
                    ),
                    "highlight": [
                        ".modal-content div[name='warehouse_id']",
                        ".modal-content div[name='date_ref']",
                        ".modal-content div[name='interval_days']",
                    ],
                    "settle": 2000,
                },
                # 3. Pivotul: produsele pe intervale de vechime, cantitate și valoare
                {
                    "url": f"{lines_url}&view_type=pivot",
                    "name": "03_pivot_vechime.png",
                    "wait": ".o_pivot",
                    "eval": self._PIVOT_ROWS_JS % "Produs",
                    "eval_wait": 2500,
                    "settle": 1500,
                },
                # 4. Lista liniilor, cu contul de stoc și data ultimei ieșiri
                {
                    "url": f"{lines_url}&view_type=list",
                    "name": "04_lista_linii.png",
                    "wait": ".o_list_view",
                    # acțiunea grupează implicit pe dată (din context, fără fațetă în căutare);
                    # desfășurăm grupurile, ca rândurile să fie la vedere
                    "eval": """async () => {
                        const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
                        for (const row of [...document.querySelectorAll('.o_list_view tr.o_group_header')]) {
                            row.click(); await sleep(700);
                        }
                    }""",
                    "eval_wait": 1500,
                    "settle": 1500,
                },
                # 5. Pivotul regrupat pe cont, pentru comparația cu balanța
                {
                    "url": f"{lines_url}&view_type=pivot",
                    "name": "05_pivot_cont.png",
                    "wait": ".o_pivot",
                    "eval": self._PIVOT_ROWS_JS % "Cont",
                    "eval_wait": 2500,
                    "settle": 1500,
                },
            ]
        )
