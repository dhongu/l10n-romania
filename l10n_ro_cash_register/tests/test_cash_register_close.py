# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import date

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestL10nRoCashRegisterClose(TransactionCase):
    """Închiderea zilei de casă: o zi închisă nu mai primește înregistrări în urmă
    (OMFP 2634/2015, Anexa 1 pct. 58 lit. d) și h))."""

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.chart_template = "ro"
        cls.cash_journal = cls.env["account.journal"].create(
            {"name": "Test Cash Close", "code": "TCCL", "type": "cash"}
        )
        cls.cash_account = cls.cash_journal.default_account_id
        cls.counterpart = cls.env["account.account"].search(
            [("company_ids", "in", cls.env.company.id), ("account_type", "=", "income")], limit=1
        )

    def _cash_move(self, day, amount):
        move = self.env["account.move"].create(
            {
                "journal_id": self.cash_journal.id,
                "date": day,
                "ref": "Test",
                "line_ids": [
                    (0, 0, {"account_id": self.cash_account.id, "debit": amount, "name": "Test"}),
                    (0, 0, {"account_id": self.counterpart.id, "credit": amount, "name": "Test"}),
                ],
            }
        )
        move.action_post()
        return move

    def _register(self, day):
        return self.env["l10n.ro.cash.register"].create({"journal_id": self.cash_journal.id, "date": day})

    def test_close_freezes_balance(self):
        self._cash_move(date(2026, 3, 2), 100.0)
        register = self._register(date(2026, 3, 2))
        register.action_close()
        self.assertEqual(register.state, "closed")
        self.assertEqual(register.closed_balance, 100.0)
        self.assertEqual(register.closed_by_id, self.env.user)

    def test_posting_on_closed_day_is_refused(self):
        self._cash_move(date(2026, 3, 2), 100.0)
        self._register(date(2026, 3, 2)).action_close()
        with self.assertRaises(UserError):
            self._cash_move(date(2026, 3, 2), 50.0)

    def test_posting_before_a_closed_day_is_refused(self):
        """O mișcare din urmă ar schimba soldul reportat în ziua închisă."""
        self._register(date(2026, 3, 5)).action_close()
        with self.assertRaises(UserError):
            self._cash_move(date(2026, 3, 3), 50.0)

    def test_posting_after_the_closed_day_is_allowed(self):
        self._register(date(2026, 3, 2)).action_close()
        move = self._cash_move(date(2026, 3, 3), 50.0)
        self.assertEqual(move.state, "posted")

    def test_draft_and_delete_of_a_closed_day_entry_are_refused(self):
        move = self._cash_move(date(2026, 3, 2), 100.0)
        register = self._register(date(2026, 3, 2))
        register.action_close()
        with self.assertRaises(UserError):
            move.button_draft()
        with self.assertRaises(UserError):
            register.unlink()

    def test_reopen_unlocks_the_day_and_the_later_ones(self):
        first = self._register(date(2026, 3, 2))
        second = self._register(date(2026, 3, 3))
        (first | second).action_close()
        first.action_reopen()
        self.assertEqual(first.state, "open")
        self.assertEqual(second.state, "open")
        move = self._cash_move(date(2026, 3, 2), 70.0)
        self.assertEqual(move.state, "posted")
        self.assertEqual(second.balance_start, 70.0)

    def test_other_cash_journal_is_not_locked(self):
        self._register(date(2026, 3, 5)).action_close()
        other = self.env["account.journal"].create({"name": "Other Cash", "code": "OCSH", "type": "cash"})
        move = self.env["account.move"].create(
            {
                "journal_id": other.id,
                "date": date(2026, 3, 3),
                "line_ids": [
                    (0, 0, {"account_id": other.default_account_id.id, "debit": 10.0, "name": "x"}),
                    (0, 0, {"account_id": self.counterpart.id, "credit": 10.0, "name": "x"}),
                ],
            }
        )
        move.action_post()
        self.assertEqual(move.state, "posted")

    def test_reversal_dated_after_the_closed_day_is_allowed(self):
        """Corecția unei zile închise se face prin stornare cu data curentă."""
        move = self._cash_move(date(2026, 3, 2), 100.0)
        self._register(date(2026, 3, 2)).action_close()
        reversal = move._reverse_moves([{"date": date(2026, 3, 10), "ref": "Storno"}])
        reversal.action_post()
        self.assertEqual(reversal.state, "posted")

    def test_inventory_correction_dated_today_is_allowed(self):
        self._register(date(2026, 3, 2)).action_close()
        correction = self._cash_move(date(2026, 3, 9), 15.0)
        self.assertEqual(correction.state, "posted")

    def test_closed_register_fields_cannot_be_changed(self):
        register = self._register(date(2026, 3, 2))
        register.action_close()
        with self.assertRaises(UserError):
            register.date = date(2026, 3, 1)
        with self.assertRaises(UserError):
            register.journal_id = self.env["account.journal"].create(
                {"name": "Other Cash 2", "code": "OCS2", "type": "cash"}
            )

    def test_future_day_cannot_be_closed(self):
        register = self._register(fields.Date.add(fields.Date.context_today(self.env.user), days=5))
        with self.assertRaises(UserError):
            register.action_close()

    def test_negative_balance_cannot_be_closed(self):
        move = self.env["account.move"].create(
            {
                "journal_id": self.cash_journal.id,
                "date": date(2026, 3, 2),
                "line_ids": [
                    (0, 0, {"account_id": self.cash_account.id, "credit": 40.0, "name": "Plată"}),
                    (0, 0, {"account_id": self.counterpart.id, "debit": 40.0, "name": "Plată"}),
                ],
            }
        )
        move.action_post()
        with self.assertRaises(UserError):
            self._register(date(2026, 3, 2)).action_close()
