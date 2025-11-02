# Copyright (C) 2025 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.tests.common import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestL10nRoCashRegister(TransactionCase):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        # Ensure RO localization behavior is active
        self.env.company.chart_template = "ro"

        # Create a cash journal; core will ensure a default liquidity account exists
        self.cash_journal = self.env["account.journal"].create(
            {
                "name": "Test Cash",
                "code": "TCAS",
                "type": "cash",
            }
        )
        self.partner = self.env["res.partner"].create({"name": "John Cash"})

    # -------------------------
    # Helpers
    # -------------------------
    def _wizard_op(self, date, amount, operation="in", description="Test Op", partner=None):
        wizard = self.env["l10n.ro.cash.register.operation"].create(
            {
                "journal_id": self.cash_journal.id,
                "date": date,
                "amount": amount,
                "operation": operation,
                "description": description,
                "partner_id": (partner or self.partner).id,
                # counterpart is defaulted, but we pass an explicit one to be safe
                "counterpart_account_id": self.env.company.transfer_account_id.id,
            }
        )
        wizard.action_confirm()
        # Return the move created on confirm (the last posted move for that date & journal account)
        move = self.env["account.move"].search(
            [
                ("journal_id", "=", self.cash_journal.id),
                ("date", "=", date),
                ("state", "=", "posted"),
            ],
            order="id desc",
            limit=1,
        )
        return move

    def _create_register(self, date):
        return self.env["l10n.ro.cash.register"].create(
            {
                "journal_id": self.cash_journal.id,
                "date": date,
            }
        )

    # -------------------------
    # Tests
    # -------------------------
    def test_register_balances_with_wizard_operations(self):
        # Previous day cash-in of 100
        self._wizard_op("2025-02-01", 100.0, operation="in", description="Opening cash in")

        # Create register for next day
        reg = self._create_register("2025-02-02")
        # At this point there is no move on 2025-02-02 yet
        self.assertAlmostEqual(reg.balance_start, 100.0, places=2)
        self.assertAlmostEqual(reg.balance_end, 100.0, places=2)

        # Now post a cash-out of 40 on the same date as register
        move_today = self._wizard_op("2025-02-02", 40.0, operation="out", description="Cash out")
        # Refresh computed fields
        reg.action_refresh()

        # Move links were computed for the register date and journal account
        self.assertIn(move_today, reg.move_ids, "Register should include today's operation move")
        # Ending balance should be 100 - 40 = 60
        self.assertAlmostEqual(reg.balance_end, 60.0, places=2)

    def test_generate_missing_registers_from_posted_moves(self):
        # Create two posted moves via wizard on different dates
        d1 = "2025-03-10"
        d2 = "2025-03-11"
        self._wizard_op(d1, 50.0, operation="in", description="d1 in")
        self._wizard_op(d2, 20.0, operation="out", description="d2 out")

        # Ensure there are no registers yet for these dates
        self.assertFalse(
            self.env["l10n.ro.cash.register"].search(
                [("journal_id", "=", self.cash_journal.id), ("date", "in", [d1, d2])]
            )
        )

        # Call generator on the journal
        self.cash_journal.generate_missing_cash_register()

        # Now both dates should have a register
        reg_d1 = self.env["l10n.ro.cash.register"].search(
            [("journal_id", "=", self.cash_journal.id), ("date", "=", d1)]
        )
        reg_d2 = self.env["l10n.ro.cash.register"].search(
            [("journal_id", "=", self.cash_journal.id), ("date", "=", d2)]
        )
        self.assertTrue(reg_d1, "Register for d1 should be generated")
        self.assertTrue(reg_d2, "Register for d2 should be generated")

        # Their balances should match move totals up to the date
        reg_d1.action_refresh()
        reg_d2.action_refresh()
        # On d1, only first move present
        self.assertAlmostEqual(reg_d1.balance_end, 50.0, places=2)
        # On d2, net is 50 - 20 = 30
        self.assertAlmostEqual(reg_d2.balance_end, 30.0, places=2)

    def test_action_contexts_and_sequence_name(self):
        reg = self._create_register("2025-04-05")

        # action_operation context
        act = reg.action_operation()
        ctx = act.get("context", {})
        self.assertEqual(ctx.get("default_journal_id"), self.cash_journal.id)
        self.assertEqual(ctx.get("default_date"), reg.date)

        # receipt and payment actions should prefill
        act_in = reg.action_receipt()
        self.assertEqual(act_in.get("context", {}).get("default_journal_id"), self.cash_journal.id)
        self.assertEqual(act_in.get("context", {}).get("default_date"), reg.date)

        act_out = reg.action_payment()
        self.assertEqual(act_out.get("context", {}).get("default_journal_id"), self.cash_journal.id)
        self.assertEqual(act_out.get("context", {}).get("default_date"), reg.date)

        # Name should be set and start with journal code
        self.assertTrue(reg.name and reg.name != "/")
        self.assertTrue(str(reg.name).startswith(self.cash_journal.code))
