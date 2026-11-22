# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import SQL

from odoo.addons.l10n_ro_stock_account.tests.common import TestROStockCommon


@tagged("post_install", "-at_install")
class TestFifoRecompute(TestROStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Without compensation, an outgoing move on negative stock keeps the
        # standard price: the kind of wrong value the recompute must find.
        cls.env.company.fifo_location_negative_compensation = False
        cls.product_fifo.standard_price = 80.0
        cls.account_valuation_wh3 = cls.env.company.account_stock_valuation_id.copy({"code": "371003"})
        cls.location2.l10n_ro_property_stock_valuation_account_id = cls.account_valuation_wh3
        cls.account_closed = cls.env["l10n.ro.fifo.recompute"]._default_account_closed() or cls.env[
            "account.account"
        ].create({"code": "117400", "name": "Closed years", "account_type": "equity"})
        cls.customers = cls.env.ref("stock.stock_location_customers")
        # Some Romanian modules refuse to post an invoice for a partner
        # without a full Romanian address (l10n_ro_efactura_enhancement).
        (cls.customer_1 | cls.supplier_1).write(
            {
                "country_id": cls.env.ref("base.ro").id,
                "state_id": cls.env.ref("base.RO_B").id,
                "city": "Sector 1",
                "street": "Strada Test 1",
            }
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _receive(self, qty, price, index, location=None):
        values = {
            "currency_id": self.ron,
            "partner_id": self.supplier_1,
            "product_id": self.product_fifo,
            "qty": qty,
            "stock_qty": qty,
            "inv_qty": qty,
            "price": price,
            "inv_price": price,
            "index": index,
        }
        if location:
            values["location"] = location
        purchase = self.create_purchase(values)
        return purchase, purchase.picking_ids.move_ids.filtered(lambda m: m.state == "done")

    def _deliver(self, qty, index):
        sale = self.create_sale_order(
            {
                "currency_id": self.ron,
                "partner_id": self.customer_1,
                "product_id": self.product_fifo,
                "qty": qty,
                "stock_qty": qty,
                "inv_qty": qty,
                "price": 150,
                "inv_price": 150,
                "advance": 0,
                "discount": 0,
                "index": index,
            }
        )
        return sale.picking_ids.move_ids.filtered(lambda m: m.product_id == self.product_fifo and m.state == "done")

    def _move(self, location_src, location_dest, qty):
        move = self.env["stock.move"].create(
            {
                "company_id": self.env.company.id,
                "location_id": location_src.id,
                "location_dest_id": location_dest.id,
                "product_id": self.product_fifo.id,
                "product_uom": self.product_fifo.uom_id.id,
                "product_uom_qty": qty,
            }
        )
        move._action_confirm()
        move._action_assign()
        move._set_quantity_done(qty)
        move.picked = True
        move._action_done()
        return move

    def _recompute(self, **vals):
        recompute = self.env["l10n.ro.fifo.recompute"].create(
            {
                "product_ids": [(6, 0, self.product_fifo.ids)],
                "account_closed_id": self.account_closed.id,
                "closed_year_date": False,
                **vals,
            }
        )
        recompute.action_compute()
        return recompute

    def _line(self, recompute, move):
        line = recompute.line_ids.filtered(lambda rec: rec.move_id == move)
        self.assertEqual(len(line), 1, f"one difference expected on {move.reference}")
        return line

    def _negative_delivery(self):
        """Deliver 3 out of an empty stock (valued at the standard price), then
        receive 5 @ 100."""
        out_move = self._deliver(3, "rc_so")
        self.assertAlmostEqual(abs(out_move.value), 3 * self.product_fifo.standard_price)
        self._receive(5, 100, "rc_po")
        return out_move

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------
    def test_ca1_difference_on_negative_delivery(self):
        """CA1: the delivery on negative stock is shown 240 -> 300, untouched."""
        out_move = self._negative_delivery()
        recompute = self._recompute()
        self.assertEqual(recompute.state, "computed")
        line = self._line(recompute, out_move)
        self.assertAlmostEqual(line.current_value, 240.0)
        self.assertAlmostEqual(line.new_value, 300.0)
        self.assertAlmostEqual(line.delta, 60.0)
        self.assertAlmostEqual(out_move.value, 240.0)
        self.assertFalse(recompute.account_move_id)

    def test_ca2_internal_transfer_and_cascade(self):
        """CA2: a transfer out of an empty warehouse is corrected between the
        stock accounts, and the delivery out of the destination follows it."""
        account_src = self.location1.l10n_ro_property_stock_valuation_account_id
        account_dest = self.location2.l10n_ro_property_stock_valuation_account_id
        transfer = self._move(self.location1, self.location2, 4)
        self.assertAlmostEqual(transfer.value, 320.0)
        self._receive(4, 100, "rc2_po", location=self.location1)
        delivery = self._move(self.location2, self.customers, 4)
        self.assertAlmostEqual(abs(delivery.value), 320.0)

        recompute = self._recompute()

        line = self._line(recompute, transfer)
        self.assertAlmostEqual(line.new_value, 400.0)
        self.assertEqual(line.account_debit_id, account_dest)
        self.assertEqual(line.account_credit_id, account_src)
        line = self._line(recompute, delivery)
        self.assertAlmostEqual(line.new_value, 400.0)
        self.assertEqual(line.account_credit_id, account_dest)
        self.assertEqual(line.account_debit_id.account_type, "expense")

    def test_ca3_customer_return_follows_delivery(self):
        """CA3: the return of a corrected delivery takes its corrected value."""
        out_move = self._negative_delivery()
        picking = out_move.picking_id
        wizard = (
            self.env["stock.return.picking"].with_context(active_id=picking.id, active_model="stock.picking").create({})
        )
        wizard.product_return_moves.quantity = 1
        return_picking = self.env["stock.picking"].browse(wizard.action_create_returns()["res_id"])
        return_picking.move_ids.quantity = 1
        return_picking.move_ids.picked = True
        return_picking.button_validate()
        return_move = return_picking.move_ids
        self.assertAlmostEqual(return_move.value, 80.0)

        recompute = self._recompute()

        line = self._line(recompute, return_move)
        self.assertAlmostEqual(line.new_value, 100.0)
        # More stock back, less cost: Dr stock / Cr expense.
        self.assertEqual(line.account_credit_id.account_type, "expense")

    def test_ca4_ca6_ca7_apply(self):
        """CA4: applying corrects the moves and posts one entry; CA6: the
        account control balances; CA7: a second run finds nothing."""
        out_move = self._negative_delivery()
        recompute = self._recompute()
        check = recompute.check_ids.filtered(
            lambda c: c.account_id == self._line(recompute, out_move).account_credit_id
        )
        self.assertEqual(len(check), 1)
        self.assertAlmostEqual(check.stock_value, 200.0)
        self.assertAlmostEqual(check.correction, -60.0)
        self.assertAlmostEqual(check.difference, 0.0)

        recompute.action_apply()

        self.assertEqual(recompute.state, "applied")
        self.assertAlmostEqual(out_move.value, 300.0)
        entry = recompute.account_move_id
        self.assertEqual(entry.state, "posted")
        self.assertEqual(entry.journal_id, self.env.company.account_stock_journal_id)
        self.assertEqual(entry.date, fields.Date.context_today(recompute))
        line = self._line(recompute, out_move)
        debit = entry.line_ids.filtered(lambda rec: rec.account_id == line.account_debit_id)
        credit = entry.line_ids.filtered(lambda rec: rec.account_id == line.account_credit_id)
        self.assertAlmostEqual(sum(debit.mapped("balance")), 60.0)
        self.assertAlmostEqual(sum(credit.mapped("balance")), -60.0)

        again = self._recompute()
        self.assertFalse(again.line_ids)

    def test_ca4_overvalued_move_in_red(self):
        """CA4: a negative difference is posted in red (storno)."""
        self.product_fifo.standard_price = 120.0
        out_move = self._negative_delivery()
        recompute = self._recompute()
        self.assertAlmostEqual(self._line(recompute, out_move).delta, -60.0)
        recompute.action_apply()
        lines = recompute.account_move_id.line_ids
        self.assertTrue(all(lines.mapped("is_storno")))
        self.assertAlmostEqual(abs(out_move.value), 300.0)

    def test_ca5_closed_year_on_closed_years_account(self):
        """CA5: a difference of a closed year goes to 1174, a transfer of the
        same period stays between the stock accounts."""
        transfer = self._move(self.location1, self.location2, 4)
        self._receive(4, 100, "rc5_po", location=self.location1)
        delivery = self._move(self.location2, self.customers, 4)

        recompute = self._recompute(closed_year_date=fields.Date.today())

        line = self._line(recompute, delivery)
        self.assertTrue(line.closed_year)
        self.assertEqual(line.account_debit_id, self.account_closed)
        line = self._line(recompute, transfer)
        self.assertNotEqual(line.account_debit_id, self.account_closed)
        self.assertNotEqual(line.account_credit_id, self.account_closed)

    def test_ca8_reception_dated_by_invoice(self):
        """CA8: a reception not made on a notice is dated by its bill: invoiced
        before the delivery, it covers the delivery even when validated after."""
        now = fields.Datetime.now()
        purchase_a, move_a = self._receive(5, 50, "rc8_a")
        purchase_b, move_b = self._receive(5, 100, "rc8_b")
        delivery = self._move(self.location, self.customers, 3)
        self.assertAlmostEqual(abs(delivery.value), 150.0)
        self.assertEqual(move_b.l10n_ro_move_type, "reception")
        # A on day -3 (billed the same day), the delivery on day -1, B received
        # today but billed on day -5.
        move_a.date = now - timedelta(days=3)
        delivery.date = now - timedelta(days=1)
        move_b.date = now
        for purchase, days in ((purchase_a, 3), (purchase_b, 5)):
            self.env.cr.execute(
                SQL(
                    "UPDATE account_move SET invoice_date = %s WHERE id IN %s",
                    (now - timedelta(days=days)).date(),
                    tuple(purchase.invoice_ids.ids),
                )
            )
        self.env.invalidate_all()

        recompute = self._recompute()

        line = self._line(recompute, delivery)
        self.assertAlmostEqual(line.new_value, 300.0)
        self.assertEqual(
            recompute._get_effective_date(move_b).date(),
            (now - timedelta(days=5)).date(),
        )

    def test_locked_correction_date_refused(self):
        """A correction date in a locked period is refused, nothing is written."""
        out_move = self._negative_delivery()
        recompute = self._recompute()
        self.env.company.fiscalyear_lock_date = recompute.date
        with self.assertRaises(UserError):
            recompute.action_apply()
        self.assertEqual(recompute.state, "computed")
        self.assertAlmostEqual(out_move.value, 240.0)
        self.assertFalse(recompute.account_move_id)

    def test_closed_year_date_needs_account(self):
        """With a closed year end and no closed years account, the compute is
        refused rather than posting a closed year on the expense account."""
        recompute = self.env["l10n.ro.fifo.recompute"].create(
            {
                "product_ids": [(6, 0, self.product_fifo.ids)],
                "closed_year_date": fields.Date.today(),
                "account_closed_id": False,
            }
        )
        with self.assertRaises(UserError):
            recompute.action_compute()

    def test_applied_recompute_not_deleted(self):
        """An applied recompute cannot be deleted."""
        self._negative_delivery()
        recompute = self._recompute()
        recompute.action_apply()
        with self.assertRaises(UserError):
            recompute.unlink()

    def test_closed_year_default_with_monthly_lock(self):
        """A lock date inside the year proposes the end of the previous year,
        a lock date at the year end proposes that year end."""
        company = self.env.company
        recompute_obj = self.env["l10n.ro.fifo.recompute"]
        year = company.compute_fiscalyear_dates(fields.Date.today())
        last_year_end = year["date_from"] - timedelta(days=1)
        company.fiscalyear_lock_date = last_year_end
        self.assertEqual(recompute_obj._default_closed_year_date(), last_year_end)
        mid_year = year["date_from"] + timedelta(days=40)
        if mid_year < fields.Date.today():
            company.fiscalyear_lock_date = mid_year
            self.assertEqual(recompute_obj._default_closed_year_date(), last_year_end)

    def test_multi_company_rule(self):
        """A run, its differences and its control are visible only in the
        companies of the user."""
        out_move = self._negative_delivery()
        recompute = self._recompute()
        self.assertTrue(recompute.line_ids.filtered(lambda r: r.move_id == out_move))
        other_company = self.env["res.company"].create({"name": "Other FIFO Co"})
        user = self.env["res.users"].create(
            {
                "name": "FIFO other company",
                "login": "fifo_other_company",
                "company_id": other_company.id,
                "company_ids": [(6, 0, other_company.ids)],
                "group_ids": [(6, 0, self.env.ref("account.group_account_manager").ids)],
            }
        )
        for model in (
            "l10n.ro.fifo.recompute",
            "l10n.ro.fifo.recompute.line",
            "l10n.ro.fifo.recompute.check",
        ):
            self.assertFalse(self.env[model].with_user(user).search([]), f"{model} leaks")

    def test_closed_year_follows_entry_date_not_invoice(self):
        """The year of a difference is the year of the original stock entry:
        a delivery booked today but invoiced before the closed year end stays
        on the expense account; the invoice date only orders the FIFO."""
        out_move = self._negative_delivery()
        today = fields.Date.today()
        invoices = out_move.sale_line_id.invoice_lines.move_id
        self.assertTrue(invoices)
        self.env.cr.execute(
            SQL(
                "UPDATE account_move SET invoice_date = %s WHERE id IN %s",
                today - timedelta(days=5),
                tuple(invoices.ids),
            )
        )
        self.env.invalidate_all()

        recompute = self._recompute(closed_year_date=today - timedelta(days=1))

        line = self._line(recompute, out_move)
        self.assertEqual(line.entry_date, out_move.account_move_id.date)
        self.assertFalse(line.closed_year)
        self.assertNotEqual(line.account_debit_id, self.account_closed)
        self.assertEqual(line.account_debit_id.account_type, "expense")

    def test_closed_year_overvalued_in_black(self):
        """An overvalued move of a closed year is corrected in black with the
        accounts swapped (Dr stock / Cr 1174), not reversed in red."""
        self.product_fifo.standard_price = 120.0
        out_move = self._negative_delivery()
        recompute = self._recompute(closed_year_date=fields.Date.today())
        line = self._line(recompute, out_move)
        self.assertTrue(line.closed_year)
        self.assertAlmostEqual(line.delta, -60.0)
        # The line shows the entry as posted: Dr stock / Cr 1174, in black.
        self.assertEqual(line.account_credit_id, self.account_closed)
        self.assertAlmostEqual(line.amount, 60.0)

        recompute.action_apply()

        entry_lines = recompute.account_move_id.line_ids
        self.assertFalse(any(entry_lines.mapped("is_storno")))
        closed_lines = entry_lines.filtered(lambda r: r.account_id == self.account_closed)
        self.assertAlmostEqual(sum(closed_lines.mapped("credit")), 60.0)
        stock_lines = entry_lines.filtered(lambda r: r.account_id == line.account_debit_id)
        self.assertAlmostEqual(sum(stock_lines.mapped("debit")), 60.0)

    def test_unflagged_internal_transfer_moves_the_stock(self):
        """An internal transfer not flagged in (inside a warehouse, or migrated
        from an older version) still moves the stock: the delivery out of its
        destination is covered by it instead of showing negative stock."""
        self._receive(10, 100, "rcu_po")
        transfer = self._move(self.location, self.location_sub_1, 6)
        self.assertEqual(transfer.l10n_ro_move_type, "internal_transfer")
        # As left by a migration: not valued, not flagged.
        self.env.cr.execute(
            SQL(
                "UPDATE stock_move SET is_in = FALSE, is_out = FALSE, value = 0 WHERE id = %s",
                transfer.id,
            )
        )
        self.env.invalidate_all()
        delivery = self._move(self.location_sub_1, self.customers, 6)

        recompute = self._recompute()

        # The delivery is covered by the transfer: no negative stock, and its
        # value (600) was already right, so it is not listed.
        self.assertFalse(recompute.line_ids.filtered(lambda r: r.move_id == delivery))
        self.assertFalse(any(recompute.line_ids.mapped("new_pending_qty")))
        line = self._line(recompute, transfer)
        self.assertAlmostEqual(line.new_value, 600.0)
        self.assertFalse(line.note)

    def test_apply_does_not_add_negative_quantity(self):
        """Applying never records a new negative quantity on a move: the engine
        would compensate it on the next incoming move of the location."""
        out_move = self._deliver(3, "rcn_so")
        self.assertFalse(out_move.fifo_neg_pending_qty)
        # A difference elsewhere so that the run has something to apply.
        transfer = self._move(self.location1, self.location2, 4)
        self._receive(4, 100, "rcn_po", location=self.location1)
        recompute = self._recompute()
        line = self._line(recompute, out_move)
        self.assertAlmostEqual(line.new_pending_qty, 3.0)
        self.assertTrue(self._line(recompute, transfer))

        recompute.action_apply()

        self.assertFalse(out_move.fifo_neg_pending_qty)

    def test_transit_legs_move_the_stock(self):
        """A transfer through transit with both legs flagged neither in nor
        out (as migrated) carries the stock and its value from the source,
        through transit, to the destination."""
        self._receive(10, 100, "rct_po")
        leg_out = self._move(self.location, self.transit_loc, 4)
        leg_in = self._move(self.transit_loc, self.location1, 4)
        self.assertEqual(leg_out.l10n_ro_move_type, "internal_transit_out")
        self.assertEqual(leg_in.l10n_ro_move_type, "internal_transit_in")
        self.env.cr.execute(
            SQL(
                "UPDATE stock_move SET is_in = FALSE, is_out = FALSE, value = 0 WHERE id IN %s",
                (leg_out.id, leg_in.id),
            )
        )
        self.env.invalidate_all()
        delivery = self._move(self.location1, self.customers, 4)

        recompute = self._recompute()

        self.assertFalse(any(recompute.line_ids.mapped("new_pending_qty")))
        self.assertAlmostEqual(self._line(recompute, leg_out).new_value, 400.0)
        self.assertAlmostEqual(self._line(recompute, leg_in).new_value, 400.0)
        delivery_line = recompute.line_ids.filtered(lambda r: r.move_id == delivery)
        if delivery_line:
            self.assertAlmostEqual(delivery_line.new_value, 400.0)
        else:
            self.assertAlmostEqual(abs(delivery.value), 400.0)
