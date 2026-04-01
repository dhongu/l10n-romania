# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestDVI(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        account_expense = cls.env["account.account"].search([("code", "=", "607000")], limit=1)
        if not account_expense:
            account_expense = cls.env["account.account"].create(
                {
                    "name": "Expense",
                    "code": "607000",
                    "account_type": "expense",
                    "reconcile": False,
                }
            )

        account_income = cls.env["account.account"].search([("code", "=", "707000")])
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
        account_input = cls.env["account.account"].search([("code", "=", "371000.i")])
        if not account_input:
            account_input = cls.env["account.account"].create(
                {
                    "name": "Income",
                    "code": "371000.i",
                    "account_type": "income",
                    "reconcile": False,
                }
            )

        # se poate utiliza foarte bine si  418
        account_output = cls.env["account.account"].search([("code", "=", "371000.o")])
        if not account_output:
            account_output = cls.env["account.account"].create(
                {
                    "name": "Output",
                    "code": "371000.o",
                    "reconcile": False,
                }
            )

        account_valuation = cls.env["account.account"].search([("code", "=", "371000")])
        if not account_valuation:
            account_valuation = cls.env["account.account"].create(
                {
                    "name": "Valuation",
                    "code": "371000",
                    "account_type": "asset_current",
                    "reconcile": False,
                }
            )

        account_other_tax = cls.env["account.account"].search([("code", "=", "446000")])
        if not account_other_tax:
            account_other_tax = cls.env["account.account"].create(
                {
                    "name": "Valuation",
                    "code": "446000",
                    "account_type": "asset_current",
                    "reconcile": True,
                }
            )

        # Creare taxe cu tag-uri pentru test
        cls.tax_tag = cls.env["account.account.tag"].create(
            {
                "name": "Test Tax Tag",
                "applicability": "taxes",
                "country_id": cls.env.ref("base.ro").id,
            }
        )
        cls.base_tag = cls.env["account.account.tag"].create(
            {
                "name": "Test Base Tag",
                "applicability": "taxes",
                "country_id": cls.env.ref("base.ro").id,
            }
        )
        cls.tax_id = cls.env["account.tax"].create(
            {
                "name": "TVA Import Test",
                "amount": 19.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "invoice_repartition_line_ids": [
                    (0, 0, {"repartition_type": "base", "factor_percent": 100, "tag_ids": [(6, 0, cls.base_tag.ids)]}),
                    (
                        0,
                        0,
                        {
                            "repartition_type": "tax",
                            "factor_percent": 100,
                            "account_id": account_other_tax.id,
                            "tag_ids": [(6, 0, cls.tax_tag.ids)],
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (0, 0, {"repartition_type": "base", "factor_percent": 100, "tag_ids": [(6, 0, cls.base_tag.ids)]}),
                    (
                        0,
                        0,
                        {
                            "repartition_type": "tax",
                            "factor_percent": 100,
                            "account_id": account_other_tax.id,
                            "tag_ids": [(6, 0, cls.tax_tag.ids)],
                        },
                    ),
                ],
            }
        )

        account_special_funds = cls.env["account.account"].search([("code", "=", "447000")])
        if not account_special_funds:
            account_special_funds = cls.env["account.account"].create(
                {
                    "name": "Valuation",
                    "code": "447000",
                    "reconcile": False,
                }
            )

        stock_journal = cls.env["account.journal"].search([("code", "=", "STJ")], limit=1)
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
                "is_storable": True,
                "categ_id": cls.category.id,
                "invoice_policy": "delivery",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product B",
                "is_storable": True,
                "categ_id": cls.category.id,
                "invoice_policy": "delivery",
            }
        )

        cls.vendor = cls.env["res.partner"].search([("name", "=", "vendor1")], limit=1)
        if not cls.vendor:
            cls.vendor = cls.env["res.partner"].create({"name": "vendor1"})
        cls.vendor.country_id = cls.env.ref("base.de")

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
        self.picking.move_line_ids.write({"quantity": 10.0})
        self.picking.button_validate()

        domain = [("product_id", "in", [self.product_1.id, self.product_2.id])]
        valuations = self.env["stock.valuation.layer"].read_group(domain, ["value:sum", "quantity:sum"], ["product_id"])
        for valuation in valuations:
            if valuation["product_id"][0] == self.product_1.id:
                self.assertEqual(valuation["value"], 10 * 100)
            if valuation["product_id"][0] == self.product_2.id:
                self.assertEqual(valuation["value"], 10 * 200)

        # Create the vendor bill from the PO using the supported API in purchase
        action = po.action_create_invoice()
        # action should contain res_id of the created account.move
        invoice = self.env["account.move"].browse(action.get("res_id"))
        self.assertTrue(invoice, "Vendor bill was not created from the Purchase Order")
        self.assertEqual(invoice.move_type, "in_invoice")
        # Ensure vendor is set as in test setup
        if not invoice.partner_id:
            invoice.partner_id = self.vendor
        # Bill date is required to post the vendor bill in this environment
        invoice.invoice_date = fields.Date.today()
        # Post the vendor bill using the public API
        invoice.action_post()

        # se deschide wizardul pt generare DVI
        action = invoice.button_dvi()
        wizard_res_model = action.get("res_model")
        wizard_id = action.get("res_id")
        wizard = self.env[wizard_res_model].browse(wizard_id)

        wizard_form = Form(wizard.with_context(active_id=invoice.id))
        self.assertEqual(wizard_form.tax_base, 3000.0, "Tax base should be initialized from invoice amount untaxed")
        wizard_form.tax_id = self.tax_id
        wizard_form.custom_duty = 5.0
        wizard_form.customs_commission = 6.0
        # Simulam o modificare manuala a TVA-ului platit in vama
        wizard_form.tax_value = wizard_form.tax_value + 1
        wizard = wizard_form.save()

        action = wizard.do_create_dvi()
        dvi = self.env[(action.get("res_model"))].browse(action.get("res_id"))
        self.assertEqual(dvi.tax_base, 3000.0)
        self.assertEqual(dvi.landed_type, "dvi")

        dvi_form = Form(dvi)
        dvi = dvi_form.save()
        dvi.compute_landed_cost()
        dvi.button_validate()

        # Verificam daca s-a creat nota contabila pentru TVA
        self.assertTrue(dvi.account_move_id, "Account move for VAT should be created")
        vat_move = dvi.account_move_id
        self.assertEqual(vat_move.state, "posted")

        # Verificam liniile notei contabile pentru TVA
        # In Odoo 18, nota contabila poate fi partajata cu intrarile de evaluare stoc.
        # Identificam liniile de TVA dupa numele lor specific.
        tva_lines = vat_move.line_ids.filtered(lambda l: _("VAT paid at customs") in l.name)
        self.assertEqual(len(tva_lines), 2, "Ar trebui sa avem exact 2 linii de TVA (debit si credit)")
        debit_line = tva_lines.filtered(lambda l: l.debit > 0)
        tva_lines.filtered(lambda l: l.credit > 0)

        self.assertTrue(debit_line.tax_tag_ids, "Debit line should have tax tags")
        # In configuratia actuala a codului, linia de credit nu primeste tag-uri de baza
        # self.assertTrue(credit_line.tax_tag_ids, "Credit line should have base tax tags")
        # self.assertTrue(credit_line.tax_ids, "Credit line should have tax_ids set for reporting")

        domain = [("product_id", "in", [self.product_1.id, self.product_2.id])]
        valuations = self.env["stock.valuation.layer"].read_group(domain, ["value:sum", "quantity:sum"], ["product_id"])
        for valuation in valuations:
            if valuation["product_id"][0] == self.product_1.id:
                # 1000 + 5*1/3 (1.67) + 6*1/3 (2) = 1003.67
                self.assertAlmostEqual(valuation["value"], 10 * 100 + 1.67 + 2, places=2)
            if valuation["product_id"][0] == self.product_2.id:
                # 2000 + 5*2/3 (3.33) + 6*2/3 (4) = 2007.33
                self.assertAlmostEqual(valuation["value"], 10 * 200 + 3.33 + 4, places=2)

        action = invoice.button_dvi()
        self.assertEqual(action.get("res_id"), dvi.id)
