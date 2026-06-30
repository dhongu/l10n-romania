# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestLandedCostIntermediary(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company

        def account(code, name, account_type="asset_current", reconcile=False):
            # Odoo 19: account.account is multi-company (company_ids); scope both the
            # lookup and the creation to the active company to avoid crossover.
            acc = cls.env["account.account"].search(
                [("code", "=", code), ("company_ids", "in", cls.company.id)], limit=1
            )
            if not acc:
                acc = cls.env["account.account"].create(
                    {
                        "name": name,
                        "code": code,
                        "account_type": account_type,
                        "reconcile": reconcile,
                        "company_ids": [(6, 0, cls.company.ids)],
                    }
                )
            return acc

        cls.account_expense = account("607000", "Expense", "expense")
        cls.account_income = account("707000", "Income", "income")
        cls.account_valuation = account("371000", "Valuation")
        cls.intermediary_account = account("482099", "Decontari costuri aditionale")

        cls.stock_journal = cls.env["account.journal"].search(
            [("code", "=", "STJ"), ("company_id", "=", cls.company.id)], limit=1
        )
        if not cls.stock_journal:
            cls.stock_journal = cls.env["account.journal"].create(
                {"name": "Stock Journal", "code": "STJ", "type": "general", "company_id": cls.company.id}
            )

        cls.category = cls.env["product.category"].create(
            {
                "name": "Marfa",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
                "property_account_income_categ_id": cls.account_income.id,
                "property_account_expense_categ_id": cls.account_expense.id,
                "property_stock_valuation_account_id": cls.account_valuation.id,
                "property_stock_journal": cls.stock_journal.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Product A", "is_storable": True, "categ_id": cls.category.id}
        )
        cls.cost_product = cls.env["product.product"].create(
            {"name": "Transport", "type": "service", "landed_cost_ok": True}
        )
        cls.vendor = cls.env["res.partner"].create({"name": "vendor_lc"})

    def _receive_product(self):
        po = Form(self.env["purchase.order"])
        po.partner_id = self.vendor
        with po.order_line.new() as po_line:
            po_line.product_id = self.product
            po_line.product_qty = 10
            po_line.price_unit = 100
        po = po.save()
        po.button_confirm()
        picking = po.picking_ids[0]
        picking.move_line_ids.write({"quantity": 10.0})
        # demo_mode bypasses the l10n_ro_edi_stock (e-Transport) carrier validation,
        # the documented escape hatch for unit tests of other modules.
        picking.with_context(demo_mode=True).button_validate()
        return picking

    def _create_landed_cost(self, picking):
        landed = self.env["stock.landed.cost"].create(
            {
                "picking_ids": [(6, 0, picking.ids)],
                "account_journal_id": self.stock_journal.id,
                "cost_lines": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.cost_product.id,
                            "price_unit": 100.0,
                            "split_method": "by_quantity",
                            "account_id": self.account_expense.id,
                        },
                    )
                ],
            }
        )
        landed.compute_landed_cost()
        landed.button_validate()
        return landed

    def test_intermediary_account_reroutes_class6(self):
        """With the intermediary method and account configured, the class 6 account
        is not credited against the stock valuation directly; the intermediary
        account nets to zero."""
        self.env.company.l10n_ro_landed_cost_method = "intermediary"
        self.env.company.l10n_ro_landed_cost_intermediary_account_id = self.intermediary_account
        landed = self._create_landed_cost(self._receive_product())
        move = landed.account_move_id
        self.assertTrue(move, "Landed cost account move should be created")

        intermediary_lines = move.line_ids.filtered(lambda line: line.account_id == self.intermediary_account)
        self.assertTrue(intermediary_lines, "Intermediary account must appear in the move")
        balance = sum(intermediary_lines.mapped("debit")) - sum(intermediary_lines.mapped("credit"))
        self.assertAlmostEqual(balance, 0.0, places=2, msg="Intermediary account must net to zero")

        class6_lines = move.line_ids.filtered(lambda line: line.account_id == self.account_expense)
        self.assertTrue(class6_lines, "Class 6 account must still be present in the move")

    def test_standard_method_keeps_standard(self):
        """With the standard method, the native behaviour is preserved
        (no intermediary account line, class 6 credited directly)."""
        self.env.company.l10n_ro_landed_cost_method = "standard"
        self.env.company.l10n_ro_landed_cost_intermediary_account_id = False
        landed = self._create_landed_cost(self._receive_product())
        move = landed.account_move_id
        self.assertTrue(move, "Landed cost account move should be created")
        intermediary_lines = move.line_ids.filtered(lambda line: line.account_id == self.intermediary_account)
        self.assertFalse(intermediary_lines, "Intermediary account must not appear when not configured")

    def test_standard_method_ignores_configured_account(self):
        """Even if an intermediary account is configured, the standard method does
        not reroute (the selector controls the behaviour, not the account)."""
        self.env.company.l10n_ro_landed_cost_method = "standard"
        self.env.company.l10n_ro_landed_cost_intermediary_account_id = self.intermediary_account
        landed = self._create_landed_cost(self._receive_product())
        move = landed.account_move_id
        intermediary_lines = move.line_ids.filtered(lambda line: line.account_id == self.intermediary_account)
        self.assertFalse(intermediary_lines, "Intermediary account must not appear under the standard method")
