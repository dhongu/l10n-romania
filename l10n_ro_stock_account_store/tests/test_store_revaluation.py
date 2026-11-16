# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from .test_store_valuation import StoreValuationCommon


@tagged("post_install", "-at_install")
class TestStoreRevaluation(StoreValuationCommon):
    """Sale price change of goods kept at sale price in a store (cost 60, price 100 + 21% VAT)."""

    def _balance(self, account):
        lines = self.env["account.move.line"].search(
            [
                ("account_id", "=", account.id),
                ("product_id", "=", self.product.id),
                ("parent_state", "=", "posted"),
            ]
        )
        return sum(lines.mapped("balance"))

    def _revaluations(self):
        return self.env["l10n.ro.store.revaluation"].search([("product_id", "=", self.product.id)])

    def _deliver(self, qty):
        return self._move(
            self.location_store,
            self.customer.property_stock_customer,
            qty,
            picking_type=self.warehouse.out_type_id,
            partner=self.customer,
        )

    def test_price_increase(self):
        """10 pcs from 100 to 120: 371 = 378 with 200 and 371 = 4428 with 42."""
        self._receive_in_store()
        self.product.list_price = 120.0
        revaluation = self._revaluations()
        self.assertRecordValues(
            revaluation,
            [
                {
                    "location_id": self.location_store.id,
                    "quantity": 10.0,
                    "old_sale_amount": 1210.0,
                    "new_sale_amount": 1452.0,
                    "old_tax_amount": 210.0,
                    "new_tax_amount": 252.0,
                    "sale_amount": 242.0,
                    "markup_amount": 200.0,
                    "tax_amount": 42.0,
                }
            ],
        )
        self.assertNotEqual(revaluation.name, "/")
        lines = revaluation.account_move_id.line_ids
        self.assertEqual(revaluation.account_move_id.state, "posted")
        self.assertEqual(revaluation.account_move_id.date, fields.Date.context_today(revaluation))
        self.assertEqual(sum(lines.filtered(lambda x: x.account_id == self.account_371).mapped("balance")), 242.0)
        self.assertEqual(sum(lines.filtered(lambda x: x.account_id == self.account_378).mapped("balance")), -200.0)
        self.assertEqual(sum(lines.filtered(lambda x: x.account_id == self.account_4428).mapped("balance")), -42.0)

    def test_exit_after_increase_releases_new_price(self):
        """After the revaluation 4 pcs leave at 120: 378 and 4428 keep exactly the markup and VAT of 6 pcs."""
        self._receive_in_store()
        self.product.list_price = 120.0
        move = self._deliver(4)
        self.assertRecordValues(
            move,
            [
                {
                    "l10n_ro_store_sale_amount": 580.8,
                    "l10n_ro_store_markup_amount": -240.0,
                    "l10n_ro_store_tax_amount": -100.8,
                }
            ],
        )
        self.assertAlmostEqual(self._balance(self.account_378), -6 * (120 - 60))
        self.assertAlmostEqual(self._balance(self.account_4428), -6 * 25.2)
        lines = move.l10n_ro_store_account_move_id.line_ids
        self.assertAlmostEqual(
            sum(lines.filtered(lambda x: x.account_id == self.account_371).mapped("balance")), -340.8
        )

    def test_price_cut_above_cost(self):
        """From 100 to 80 (cost 60): the reverse entry in black, 378 = 371 and 4428 = 371."""
        self._receive_in_store()
        self.product.list_price = 80.0
        revaluation = self._revaluations()
        self.assertRecordValues(revaluation, [{"sale_amount": -242.0, "markup_amount": -200.0, "tax_amount": -42.0}])
        lines = revaluation.account_move_id.line_ids
        self.assertTrue(all(line.debit >= 0 and line.credit >= 0 for line in lines))
        self.assertEqual(sum(lines.filtered(lambda x: x.account_id == self.account_371).mapped("credit")), 242.0)
        self.assertEqual(sum(lines.filtered(lambda x: x.account_id == self.account_378).mapped("debit")), 200.0)
        self.assertEqual(sum(lines.filtered(lambda x: x.account_id == self.account_4428).mapped("debit")), 42.0)

    def test_price_cut_below_cost_is_blocked(self):
        self._receive_in_store()
        with self.assertRaises(UserError):
            self.product.list_price = 50.0
        self.assertFalse(self._revaluations())

    def test_no_revaluation_without_store_stock(self):
        self._move(
            self.supplier.property_stock_supplier,
            self.location_depot,
            10,
            60.0,
            self.warehouse.in_type_id,
            self.supplier,
        )
        self.product.list_price = 120.0
        self.assertFalse(self._revaluations())

    def test_same_price_no_revaluation(self):
        self._receive_in_store()
        self.product.list_price = 100.0
        self.assertFalse(self._revaluations())

    def test_two_changes_and_back(self):
        """100 -> 120 -> 100: two revaluations, 378 and 4428 back to the entry values."""
        self._receive_in_store()
        self.product.list_price = 120.0
        self.product.list_price = 100.0
        self.assertEqual(len(self._revaluations()), 2)
        self.assertAlmostEqual(self._balance(self.account_378), -400.0)
        self.assertAlmostEqual(self._balance(self.account_4428), -210.0)

    def test_locked_period_refuses_price_change(self):
        self._receive_in_store()
        self.env.company.fiscalyear_lock_date = fields.Date.context_today(self.env.company)
        with self.assertRaises(UserError):
            self.product.list_price = 120.0

    def test_store_pricelist_keeps_store_price(self):
        """A store with a fixed price in its pricelist: a change of the product price does not
        change the store price, so there is nothing to revaluate."""
        if "store_pricelist_id" not in self.location_store._fields:
            self.skipTest("l10n_ro_picking_report not installed")
        self.location_store.store_pricelist_id = self.env["product.pricelist"].create(
            {
                "name": "Preturi magazin",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "0_product_variant",
                            "product_id": self.product.id,
                            "compute_price": "fixed",
                            "fixed_price": 120.0,
                        },
                    )
                ],
            }
        )
        self._receive_in_store()
        self.product.list_price = 130.0
        self.assertFalse(self._revaluations())

    def _return(self, moves, qty, dest=None):
        wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=moves.picking_id.id, active_model="stock.picking")
            .create({})
        )
        wizard.product_return_moves.quantity = qty
        return_picking = wizard._create_return()
        if dest:
            return_picking.location_dest_id = dest
            return_picking.move_ids.location_dest_id = dest
        return_picking.move_ids.quantity = qty
        return_picking.move_ids.picked = True
        return_picking.button_validate()
        return return_picking.move_ids

    def test_revaluation_documents_old_price_and_user(self):
        self._receive_in_store()
        self.product.list_price = 120.0
        self.assertRecordValues(
            self._revaluations(), [{"old_price": 100.0, "new_price": 120.0, "user_id": self.env.user.id}]
        )

    def test_customer_return_after_revaluation(self):
        """3 pcs sold at 100, price raised to 120, 1 pc returned at 100: the store is brought back
        to 120 and, once all is sold, 378 and 4428 are closed."""
        self._receive_in_store()
        delivery = self._deliver(3)
        self.product.list_price = 120.0
        customer_return = self._return(delivery, 1, dest=self.location_store)
        realign = self._revaluations().filtered("origin_move_id")
        self.assertEqual(realign.origin_move_id, customer_return)
        self.assertRecordValues(realign, [{"quantity": 8.0, "sale_amount": 24.2, "tax_amount": 4.2}])
        self._deliver(8)
        self.assertAlmostEqual(self._balance(self.account_378), 0.0)
        self.assertAlmostEqual(self._balance(self.account_4428), 0.0)

    def test_supplier_return_after_revaluation(self):
        """Price raised to 120, 2 pcs returned to the supplier at the reception price: the 8 pcs left
        are brought back to 120 and close 378 and 4428 when sold."""
        reception = self._receive_in_store()
        self.product.list_price = 120.0
        self._return(reception, 2)
        realign = self._revaluations().filtered("origin_move_id")
        self.assertRecordValues(realign, [{"quantity": 8.0, "sale_amount": -48.4, "tax_amount": -8.4}])
        self._deliver(8)
        self.assertAlmostEqual(self._balance(self.account_378), 0.0)
        self.assertAlmostEqual(self._balance(self.account_4428), 0.0)

    def test_stock_not_booked_at_sale_price_is_not_revalued(self):
        """Stock put in the store without a store entry (e.g. before the module) has no markup to revalue."""
        self.env["stock.quant"]._update_available_quantity(self.product, self.location_store, 5)
        self.product.list_price = 120.0
        self.assertFalse(self._revaluations())

    def test_last_exit_closes_the_store_balance(self):
        """3 pcs at 99.99 + 21%: the exits by ratio would leave cents; the last one closes 378 and 4428."""
        self.product.list_price = 99.99
        self._receive_in_store(qty=3)
        self.product.list_price = 120.01
        self._deliver(1)
        self._deliver(1)
        self._deliver(1)
        self.assertAlmostEqual(self._balance(self.account_378), 0.0)
        self.assertAlmostEqual(self._balance(self.account_4428), 0.0)
