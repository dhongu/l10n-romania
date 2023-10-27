# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestDVI(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestDVI, cls).setUpClass()

        company = cls.env.company
        domain = [("company_id", "=", company.id),("code", "=", "607000")]
        account_expense = cls.env["account.account"].search(domain, limit=1)
        if not account_expense:
            account_expense = cls.env["account.account"].create(
                {
                    "name": "Expense",
                    "code": "607000",
                    "account_type": "expense",
                    "reconcile": False,
                }
            )
        domain = [("company_id", "=", company.id),("code", "=", "707000")]
        account_income = cls.env["account.account"].search(domain, limit=1)
        if not account_income:
            account_income = cls.env["account.account"].create(
                {
                    "name": "Income",
                    "code": "707000",
                    "account_type": "income",
                    "reconcile": False,
                }
            )

        # se poate utiliza foarte bine si  408
        domain = [("company_id", "=", company.id),("code", "=", "371000.i")]
        account_input = cls.env["account.account"].search(domain, limit=1)
        if not account_input:
            account_input = cls.env["account.account"].create(
                {
                    "name": "Income",
                    "code": "371000.i",
                    "account_type": "asset_current",
                    "reconcile": False,
                }
            )

        # se poate utiliza foarte bine si  418
        domain = [("company_id", "=", company.id),("code", "=", "371000.o")]
        account_output = cls.env["account.account"].search(domain, limit=1)
        if not account_output:
            account_output = cls.env["account.account"].create(
                {
                    "name": "Output",
                    "code": "371000.o",
                    "account_type": "asset_current",
                    "reconcile": False,
                }
            )
        domain = [("company_id", "=", company.id),("code", "=", "371000")]
        account_valuation = cls.env["account.account"].search(domain, limit=1)
        if not account_valuation:
            account_valuation = cls.env["account.account"].create(
                {
                    "name": "Valuation",
                    "code": "371000",
                    "account_type": "asset_current",
                    "reconcile": False,
                }
            )
        domain = [("company_id", "=", company.id),("code", "=", "446000")]
        account_other_tax = cls.env["account.account"].search(domain, limit=1)
        if not account_other_tax:
            account_other_tax = cls.env["account.account"].create(
                {
                    "name": "Valuation",
                    "code": "446000",
                    "account_type": "asset_current",
                    "reconcile": True,
                }
            )
        domain = [("company_id", "=", company.id),("code", "=", "447000")]
        account_special_funds = cls.env["account.account"].search(domain, limit=1)
        if not account_special_funds:
            account_special_funds = cls.env["account.account"].create(
                {
                    "name": "Valuation",
                    "code": "447000",
                    "account_type": "asset_current",
                    "reconcile": False,
                }
            )
        domain = [("company_id", "=", company.id),("code", "=", "STJ")]
        stock_journal = cls.env["account.journal"].search(domain, limit=1)
        if not stock_journal:
            stock_journal = cls.env["account.journal"].create(
                {"name": "Stock Journal", "code": "STJ", "type": "general"}
            )

        cls.category = cls.env["product.category"].create(
            {
                "name": "Marfa",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
                "property_account_income_categ_id": account_income.id,
                "property_account_expense_categ_id": account_expense.id,
                "property_stock_account_input_categ_id": account_input.id,
                "property_stock_account_output_categ_id": account_output.id,
                "property_stock_valuation_account_id": account_valuation.id,
                "property_stock_journal": stock_journal.id,
            }
        )

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": cls.category.id,
                "invoice_policy": "delivery",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "categ_id": cls.category.id,
                "invoice_policy": "delivery",
            }
        )

        cls.vendor = cls.env["res.partner"].search([("name", "=", "vendor1")], limit=1)
        if not cls.vendor:
            cls.vendor = cls.env["res.partner"].create({"name": "vendor1"})

    def test_call_wizard(self):
        po = Form(self.env["purchase.order"])
        po.partner_id = self.vendor
        with po.order_line.new() as po_line:
            po_line.product_id = self.product_1
            po_line.product_qty = 10
            po_line.price_unit = 100
        with po.order_line.new() as po_line:
            po_line.product_id = self.product_2
            po_line.product_qty = 10
            po_line.price_unit = 200
        po = po.save()
        po.button_confirm()
        self.picking = po.picking_ids[0]
        self.picking.move_line_ids.write({"qty_done": 10.0})
        self.picking.button_validate()

        domain = [("product_id", "in", [self.product_1.id, self.product_2.id])]
        valuations = self.env["stock.valuation.layer"].read_group(domain, ["value:sum", "quantity:sum"], ["product_id"])
        for valuation in valuations:
            if valuation["product_id"][0] == self.product_1.id:
                self.assertEqual(valuation["value"], 10 * 100)
            if valuation["product_id"][0] == self.product_2.id:
                self.assertEqual(valuation["value"], 10 * 200)

        invoice = Form(self.env["account.move"].with_context(default_move_type="in_invoice"))
        invoice.partner_id = self.vendor
        invoice.purchase_id = po

        invoice = invoice.save()
        invoice.post()

        # se deschide wizardul pt generare DVI
        action = invoice.button_dvi()
        wizard = self.env[(action.get("res_model"))].browse(action.get("res_id"))

        wizard = Form(wizard.with_context({"active_id": invoice.id}))
        wizard.custom_duty = 5.0
        wizard.customs_commission = 6.0
        wizard.tax_value = wizard.tax_value + 1
        wizard = wizard.save()

        action = wizard.do_create_dvi()
        dvi = self.env[(action.get("res_model"))].browse(action.get("res_id"))
        dvi = Form(dvi)
        dvi = dvi.save()
        dvi.compute_landed_cost()
        dvi.button_validate()

        domain = [("product_id", "in", [self.product_1.id, self.product_2.id])]
        valuations = self.env["stock.valuation.layer"].read_group(domain, ["value:sum", "quantity:sum"], ["product_id"])
        for valuation in valuations:
            if valuation["product_id"][0] == self.product_1.id:
                self.assertEqual(valuation["value"], 10 * 100 + 1.67 + 2)
            if valuation["product_id"][0] == self.product_2.id:
                self.assertEqual(valuation["value"], 10 * 200 + 3.33 + 4)

        action = invoice.button_dvi()
        self.assertEqual(action.get("res_id"), dvi.id)
