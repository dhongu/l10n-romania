# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import logging
import time

from odoo.tests import Form
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestStorageSheet(TransactionCase):
    def setUp(self):
        super().setUp()

        self.account_difference = self.env["account.account"].search([("code", "=", "348000")])
        self.account_expense = self.env["account.account"].search([("code", "=", "607000")])
        self.account_income = self.env["account.account"].search([("code", "=", "707000")])
        self.account_valuation = self.env["account.account"].search([("code", "=", "371000")])

        stock_journal = self.env["account.journal"].search([("code", "=", "STJ")])
        if not stock_journal:
            stock_journal = self.env["account.journal"].create(
                {"name": "Stock Journal", "code": "STJ", "type": "general"}
            )

        property_diff = "property_account_creditor_price_difference_categ"

        category_value = {
            "name": "TEST Marfa",
            "property_cost_method": "fifo",
            "property_valuation": "real_time",
            property_diff: self.account_difference.id,
            "property_account_income_categ_id": self.account_income.id,
            "property_account_expense_categ_id": self.account_expense.id,
            "property_stock_account_input_categ_id": self.account_expense.id,
            "property_stock_account_output_categ_id": self.account_income.id,
            "property_stock_valuation_account_id": self.account_valuation.id,
            "property_stock_journal": stock_journal.id,
        }

        self.category = self.env["product.category"].search([("name", "=", "TEST Marfa")])
        if not self.category:
            self.category = self.env["product.category"].create(category_value)
        else:
            self.category.write(category_value)

        self.price_p1 = 50.0
        self.list_price_p1 = 70.0
        # cantitatea din PO
        self.qty_po_p1 = 20.0

        self.product_1 = self.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": self.category.id,
                "invoice_policy": "delivery",
                "purchase_method": "receive",
                "list_price": self.list_price_p1,
                "standard_price": self.price_p1,
            }
        )
        Partner = self.env["res.partner"]
        self.vendor = Partner.search([("name", "=", "TEST Vendor")], limit=1)
        if not self.vendor:
            self.vendor = Partner.create({"name": "TEST Vendor"})

        self.client = Partner.search([("name", "=", "TEST Client")], limit=1)
        if not self.client:
            self.client = Partner.create({"name": "TEST Client"})

        picking_type_in = self.env.ref("stock.picking_type_in")
        self.location = picking_type_in.default_location_dest_id

        date_range = self.env["date.range"]
        self.type = self.env["date.range.type"].create({"name": "Month", "company_id": False, "allow_overlap": False})
        self.dt = date_range.create(
            {
                "name": "FS2016",
                "date_start": time.strftime("%Y-%m-01"),
                "date_end": time.strftime("%Y-%m-28"),
                "type_id": self.type.id,
            }
        )

    def create_po(self, picking_type_in=None):
        po = Form(self.env["purchase.order"])
        po.partner_id = self.vendor

        with po.order_line.new() as po_line:
            po_line.product_id = self.product_1
            po_line.product_qty = self.qty_po_p1
            po_line.price_unit = self.price_p1

        po = po.save()
        po.button_confirm()
        self.picking = po.picking_ids[0]

        for move_line in self.picking.move_line_ids:
            if move_line.product_id == self.product_1:
                move_line.write({"qty_done": self.qty_po_p1})

        self.picking.button_validate()
        _logger.info("Receptie facuta")

        self.po = po
        return po

    def create_invoice(self):
        AccountMove = self.env["account.move"]
        invoice = Form(AccountMove.with_context(default_type="in_invoice"))
        invoice.partner_id = self.vendor
        invoice.purchase_id = self.po
        invoice = invoice.save()
        invoice.post()
        _logger.info("Factura introdusa")

    def test_report_storage_sheet(self):
        self.create_po()
        self.create_invoice()

        wizard = Form(self.env["stock.storage.sheet.report"])
        wizard.product_id = self.product_1
        wizard.location_id = self.location
        wizard.date_range_id = self.dt
        wizard = wizard.save()
        wizard.do_compute()
        wizard.button_show()
        wizard.button_print()

        line = self.env["stock.storage.sheet.report.line"].search([("report_id", "=", wizard.id)], limit=1)
        line.action_valuation_at_date_details()

    def test_report_daily_stock(self):
        self.create_po()
        self.create_invoice()

        wizard = Form(self.env["stock.daily.stock.report"].with_context(default_mode="product"))

        wizard.location_id = self.location
        wizard.mode = "product"
        wizard = wizard.save()
        wizard.button_show()
        wizard.button_print()
        line = self.env["stock.daily.stock.report.line"].search([("report_id", "=", wizard.id)], limit=1)
        line.action_valuation_at_date_details()

        wizard = Form(self.env["stock.daily.stock.report"])
        wizard.date_range_id = self.dt
        wizard.location_id = self.location
        wizard.mode = "ref"
        wizard = wizard.save()
        wizard.button_show()
        wizard.button_print()
        line = self.env["stock.daily.stock.report.ref"].search([("report_id", "=", wizard.id)], limit=1)
        line.action_valuation_at_date_details()
