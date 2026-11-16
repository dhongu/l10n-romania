# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Capturi de ecran pentru fișa „Dropship în fișa de magazie (stiva OCA)”.
# Seedează o vânzare cu ruta Dropship, confirmă achiziția generată și validează transferul
# dropship, apoi calculează fișa de magazie OCA pe luna curentă.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_stock_report_dropship,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import unittest

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestDropshipScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_report_dropship"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Firma Demo SRL")
        company = cls.env.company
        company.write({"l10n_ro_accounting": True, "anglo_saxon_accounting": True})
        admin = cls.env.ref("base.user_admin")
        admin.write({"company_ids": [(4, company.id)], "company_id": company.id})
        for xmlid in (
            "stock.group_stock_manager",
            "stock.group_adv_location",
            "purchase.group_purchase_manager",
            "sales_team.group_sale_manager",
            "account.group_account_manager",
            "l10n_ro_config.group_ro_menus",
        ):
            # admin pentru browser, utilizatorul testului pentru seed
            (admin | cls.env.user).group_ids = [(4, cls.env.ref(xmlid).id)]

        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        # codul implicit al depozitului e luat din numele companiei de test („compa”)
        cls.warehouse.write({"name": "Depozit central", "code": "DEP"})
        ref = cls.env["account.chart.template"].with_company(company).ref
        category = cls.env["product.category"].create(
            {
                "name": "Mărfuri",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": ref("pcg_371").id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Imprimantă laser A4",
                "is_storable": True,
                "categ_id": category.id,
                "list_price": 900.0,
                # costul produsului diferă de prețul de achiziție: valoarea dropship vine din achiziție
                "standard_price": 550.0,
            }
        )
        vendor = cls.env["res.partner"].create({"name": "Furnizor Demo SRL"})
        customer = cls.env["res.partner"].create({"name": "Client Demo SRL"})
        cls.env["product.supplierinfo"].create(
            {"partner_id": vendor.id, "product_tmpl_id": cls.product.product_tmpl_id.id, "price": 600.0}
        )

        so_form = Form(cls.env["sale.order"])
        so_form.partner_id = customer
        with so_form.order_line.new() as line:
            line.product_id = cls.product
            line.product_uom_qty = 5
        sale = so_form.save()
        sale.order_line.route_ids = cls.env.ref("stock_dropshipping.route_drop_shipping")
        sale.action_confirm()
        purchase = cls.env["purchase.order"].search([("origin", "=", sale.name)])
        purchase.button_confirm()
        cls.picking = purchase.picking_ids
        cls.picking.move_ids.quantity = 5
        cls.picking.move_ids.picked = True
        cls.picking.button_validate()
        # factura furnizorului (Dr 371 + 4426 = 401): intrarea în 371 pe care o compensează transferul
        bill_action = purchase.action_create_invoice()
        cls.bill = cls.env["account.move"].browse(bill_action["res_id"])
        cls.bill.invoice_date = cls.bill.date = cls.picking.date_done.date()
        cls.bill.action_post()

        wizard_form = Form(cls.env["l10n.ro.stock.storage.sheet"])
        wizard_form.location_id = cls.warehouse.lot_stock_id
        cls.wizard = wizard_form.save()
        cls.wizard.do_compute_product()
        cls.wizard_action = cls.env.ref("l10n_ro_stock_report.action_sheet_stock_report").id

    def _shots(self):
        return [
            {
                "url": f"id={self.picking.id}&model=stock.picking&view_type=form",
                "name": "01_transfer_dropship.png",
                "wait": ".o_form_view",
                "highlight": ["div[name='partner_id']", "div[name='picking_type_id']"],
                "hide_chatter": True,
                "settle": 2000,
            },
            self.account_move_shot(self.picking.move_ids.account_move_id, "02_nota_dropship.png"),
            {
                "url": f"action={self.wizard_action}&id={self.wizard.id}&model=l10n.ro.stock.storage.sheet&view_type=form",
                "name": "03_lista_fisa_dropship.png",
                "wait": ".o_form_view",
                "click_btn": "button[name='button_show_sheet']",
                "wait_after": ".o_pivot",
                "eval": "document.querySelector('.o_switch_view.o_list')?.click();",
                "settle": 3000,
            },
            self.report_shot("l10n_ro_stock_report.report_storage_sheet_all", self.wizard, "04_pdf_fisa_dropship.png"),
        ]

    def test_capture_fise(self):
        self.capture_screenshots(self._shots(), hide_systray=True)

    def test_capture_usage(self):
        self.capture_screenshots(self._shots(), hide_systray=True, lang="en_US")
