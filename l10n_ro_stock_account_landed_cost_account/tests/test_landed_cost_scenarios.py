# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from .test_landed_cost_intermediary import TestLandedCostIntermediary


@tagged("post_install", "-at_install")
class TestLandedCostScenarios(TestLandedCostIntermediary):
    """Landed cost scenarios used by the consultant sheet:
    full purchase flow from the vendor bill, stock reserved for a sale,
    stock already sold."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # A Romanian company: the receipts, deliveries and landed cost use the
        # Romanian stock accounting (l10n_ro_stock_account).
        cls.company.write({"country_id": cls.env.ref("base.ro").id, "l10n_ro_accounting": True})

    def _lines(self, move):
        return sorted((line.account_id.code, line.debit, line.credit) for line in move.line_ids)

    def _enable_intermediary(self):
        self.env.company.l10n_ro_landed_cost_method = "intermediary"
        self.env.company.l10n_ro_landed_cost_intermediary_account_id = self.intermediary_account

    def _purchase_receipt(self, qty=10.0):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create({"product_id": self.product.id, "product_qty": qty, "price_unit": 100.0})
                ],
            }
        )
        po.button_confirm()
        picking = po.picking_ids[0]
        picking.move_line_ids.write({"quantity": qty})
        picking.with_context(demo_mode=True).button_validate()
        return po, picking

    def _delivery(self, qty, validate):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.env.ref("stock.stock_location_stock").id,
                            "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        if validate:
            picking.move_line_ids.write({"quantity": qty})
            picking.with_context(demo_mode=True).button_validate()
        return picking

    def _transport_bill(self, amount=100.0):
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "invoice_date": "2026-11-11",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.cost_product.id,
                            "quantity": 1,
                            "price_unit": amount,
                            "account_id": self.account_expense.id,
                            "is_landed_costs_line": True,
                        }
                    )
                ],
            }
        )
        bill.action_post()
        return bill

    def _landed_from_bill(self, picking, amount=100.0):
        """Landed cost created with the bill button; the bill has no purchase order,
        so the receipt is added by hand, as the consultant does."""
        bill = self._transport_bill(amount)
        landed = self.env["stock.landed.cost"].browse(bill.button_create_landed_costs()["res_id"])
        self.assertEqual(landed.cost_lines.account_id, self.account_expense)
        landed.write({"picking_ids": [Command.set(picking.ids)], "account_journal_id": self.stock_journal.id})
        landed.compute_landed_cost()
        landed.button_validate()
        return landed

    # Scenario 1: the full flow (as in deltatech_obyc_landed_cost)
    def test_01_flow_standard(self):
        """PO -> receipt -> goods bill -> transport bill -> landed cost: Dr 371 / Cr 6xx."""
        po, receipt = self._purchase_receipt()
        goods_bill = self.env["account.move"].browse(po.action_create_invoice()["res_id"])
        goods_bill.invoice_date = "2026-11-11"
        goods_bill.action_post()
        self.assertEqual(
            goods_bill.line_ids.filtered(lambda line: line.account_id == self.account_valuation).debit, 1000
        )
        landed = self._landed_from_bill(receipt)
        self.assertEqual(landed.state, "done")
        self.assertEqual(landed.account_move_id.journal_id, self.stock_journal)
        self.assertEqual(self._lines(landed.account_move_id), [("371000", 100.0, 0.0), ("607000", 0.0, 100.0)])
        self.assertAlmostEqual(receipt.move_ids.value, 1100.0)

    def test_02_flow_intermediary(self):
        """Same flow, through the intermediary account: two balanced pairs."""
        self._enable_intermediary()
        __, receipt = self._purchase_receipt()
        landed = self._landed_from_bill(receipt)
        self.assertEqual(
            self._lines(landed.account_move_id),
            [("371000", 100.0, 0.0), ("482099", 0.0, 100.0), ("482099", 100.0, 0.0), ("607000", 0.0, 100.0)],
        )

    # Scenario 2: stock already reserved for a sale
    def test_03_reserved_stock_capitalized_fully(self):
        """Reserved stock is still in stock: the whole cost is capitalized and follows
        the goods into the cost of sales when the delivery is validated."""
        __, receipt = self._purchase_receipt()
        delivery = self._delivery(4.0, validate=False)
        self.assertEqual(delivery.state, "assigned")
        landed = self._landed_from_bill(receipt)
        self.assertEqual(self._lines(landed.account_move_id), [("371000", 100.0, 0.0), ("607000", 0.0, 100.0)])
        self.assertEqual(delivery.state, "assigned", "The reservation is not touched")
        delivery.move_line_ids.write({"quantity": 4.0})
        delivery.with_context(demo_mode=True).button_validate()
        self.assertAlmostEqual(delivery.move_ids.value, 440.0, msg="4 pcs leave at 110 (100 + 10 landed cost)")

    # Scenario 3: stock already sold
    def test_04_sold_stock_partially_capitalized(self):
        """4 of 10 pcs were sold before the landed cost: only the 6 in stock are
        capitalized (60 of 100); the delivery keeps its cost and 40 stay on class 6."""
        __, receipt = self._purchase_receipt()
        delivery = self._delivery(4.0, validate=True)
        self.assertEqual(delivery.move_ids.value, 400.0)
        landed = self._landed_from_bill(receipt)
        self.assertEqual(self._lines(landed.account_move_id), [("371000", 60.0, 0.0), ("607000", 0.0, 60.0)])
        self.assertEqual(delivery.move_ids.value, 400.0, "The delivered cost is not restated")

    def test_05_sold_stock_intermediary(self):
        self._enable_intermediary()
        __, receipt = self._purchase_receipt()
        self._delivery(4.0, validate=True)
        landed = self._landed_from_bill(receipt)
        self.assertEqual(
            self._lines(landed.account_move_id),
            [("371000", 60.0, 0.0), ("482099", 0.0, 60.0), ("482099", 60.0, 0.0), ("607000", 0.0, 60.0)],
        )

    def test_06_everything_sold_no_capitalization(self):
        """All the goods were sold: nothing is capitalized, the cost stays on class 6."""
        __, receipt = self._purchase_receipt()
        self._delivery(10.0, validate=True)
        landed = self._landed_from_bill(receipt)
        self.assertEqual(landed.state, "done")
        self.assertFalse(landed.account_move_id.line_ids)
