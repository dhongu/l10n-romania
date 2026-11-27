# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
# Capturi de ecran pentru fișa „Fișa de magazie”.
# Seedează o recepție (comandă de achiziție) și o livrare (comandă de vânzare) pentru două
# produse în depozitul principal, apoi fișa de magazie pe luna curentă.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_storage_sheet,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import unittest

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


PIVOT_BY_PRODUCT = """
    const closed = [...document.querySelectorAll('.o_pivot_header_cell_closed')];
    const opened = [...document.querySelectorAll('.o_pivot_header_cell_opened')];
    const rowHeader = opened.find((el) => el.closest('tbody'));
    if (rowHeader) {
        rowHeader.click();
        setTimeout(() => {
            const total = [...document.querySelectorAll('tbody .o_pivot_header_cell_closed')][0];
            total?.click();
            setTimeout(() => {
                const item = [...document.querySelectorAll('.o-dropdown-item, .dropdown-item')]
                    .find((el) => ['Produs', 'Product'].includes(el.textContent.trim()));
                item?.click();
            }, 1200);
        }, 1200);
    }
"""


@tagged("-at_install", "post_install", "fise_screenshots")
class TestStorageSheetScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_storage_sheet"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Firma Demo SRL")
        company = cls.env.company
        admin = cls.env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        for xmlid in ("stock.group_stock_manager", "purchase.group_purchase_manager", "sales_team.group_sale_manager"):
            # admin pentru browser, utilizatorul testului pentru seed
            (admin | cls.env.user).group_ids = [(4, cls.env.ref(xmlid).id)]

        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        # codul implicit al depozitului e luat din numele companiei de test („compa”)
        cls.warehouse.write({"name": "Depozit central", "code": "DEP"})
        cls.location = cls.warehouse.lot_stock_id
        # mărfuri: contul de stoc 371, nu contul implicit al companiei (301 Materii prime)
        account_371 = cls.env["account.chart.template"].with_company(company).ref("pcg_371")
        category = cls.env["product.category"].create(
            {"name": "Mărfuri", "property_stock_valuation_account_id": account_371.id}
        )
        Product = cls.env["product.product"]
        product_vals = {"is_storable": True, "categ_id": category.id}
        cls.cable = Product.create({**product_vals, "name": "Cablu UTP Cat6", "standard_price": 2.5, "list_price": 4.0})
        cls.plug = Product.create({**product_vals, "name": "Mufă RJ45", "standard_price": 0.4, "list_price": 1.0})
        cls.vendor = cls.env["res.partner"].create({"name": "Furnizor Demo SRL"})
        cls.customer = cls.env["res.partner"].create({"name": "Client Demo SRL"})

        po_form = Form(cls.env["purchase.order"])
        po_form.partner_id = cls.vendor
        for product, qty, price in ((cls.cable, 100, 2.5), (cls.plug, 200, 0.4)):
            with po_form.order_line.new() as line:
                line.product_id = product
                line.product_qty = qty
                line.price_unit = price
        purchase = po_form.save()
        purchase.button_confirm()
        cls._validate(purchase.picking_ids)
        # recepția în luna anterioară, ca fișa lunii curente să aibă sold inițial
        receipt_date = fields.Datetime.now().replace(day=1) - relativedelta(days=5)
        purchase.picking_ids.write({"date_done": receipt_date})
        purchase.picking_ids.move_ids.write({"date": receipt_date})
        purchase.picking_ids.move_ids.move_line_ids.write({"date": receipt_date})

        so_form = Form(cls.env["sale.order"])
        so_form.partner_id = cls.customer
        for product, qty in ((cls.cable, 30), (cls.plug, 50)):
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        sale = so_form.save()
        sale.action_confirm()
        cls._validate(sale.picking_ids)

        wizard_form = Form(cls.env["l10n.ro.storage.sheet"])
        wizard_form.location_id = cls.location
        cls.wizard = wizard_form.save()
        cls.wizard.do_compute_product()
        cls.wizard_action = cls.env.ref("l10n_ro_storage_sheet.action_sheet_stock_report").id

    @classmethod
    def _validate(cls, pickings):
        for move in pickings.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        pickings.button_validate()

    def _wizard_url(self):
        return f"action={self.wizard_action}&id={self.wizard.id}&model=l10n.ro.storage.sheet&view_type=form"

    def _shots(self):
        return [
            {
                "url": self._wizard_url(),
                "name": "01_wizard_fisa_magazie.png",
                "wait": ".o_form_view",
                "highlight": [
                    "div[name='location_id']",
                    "div[name='date_from']",
                    "button[name='button_show_sheet']",
                ],
                "settle": 2000,
            },
            {
                "url": self._wizard_url(),
                "name": "02_pivot_fisa_magazie.png",
                "wait": ".o_form_view",
                "click_btn": "button[name='button_show_sheet']",
                "wait_after": ".o_pivot",
                # rândurile pivotului: pe produs, în loc de cont
                "eval": PIVOT_BY_PRODUCT,
                "settle": 5000,
            },
            {
                "url": self._wizard_url(),
                "name": "03_lista_miscari.png",
                "wait": ".o_form_view",
                "click_btn": "button[name='button_show_sheet']",
                "wait_after": ".o_pivot",
                "eval": "document.querySelector('.o_switch_view.o_list')?.click();",
                "settle": 3000,
            },
            # fișa tipărită (Tipărire fișă, fără „O pagină per produs”)
            self.report_shot("l10n_ro_storage_sheet.report_storage_sheet_all", self.wizard, "04_pdf_fisa_magazie.png"),
        ]

    def test_capture_fise(self):
        self.capture_screenshots(self._shots(), hide_systray=True)

    def test_capture_usage(self):
        self.capture_screenshots(self._shots(), hide_systray=True, lang="en_US")
