# Copyright (C) 2025 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
from datetime import date

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestCashRegisterSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        # Create two distinct cash accounts
        cls.acc_cash_a = cls.env["account.account"].create(
            {
                "name": "Cash A",
                "code": "1010A",
                "account_type": "asset_cash",
            }
        )
        cls.acc_cash_b = cls.env["account.account"].create(
            {
                "name": "Cash B",
                "code": "1010B",
                "account_type": "asset_cash",
            }
        )

        # Create two cash journals with different codes
        cls.journal_a = cls.env["account.journal"].create(
            {
                "name": "Cash Journal A",
                "code": "CASH",
                "type": "cash",
                "company_id": cls.company.id,
                "default_account_id": cls.acc_cash_a.id,
            }
        )
        cls.journal_b = cls.env["account.journal"].create(
            {
                "name": "Cash Journal B",
                "code": "PETY",
                "type": "cash",
                "company_id": cls.company.id,
                "default_account_id": cls.acc_cash_b.id,
            }
        )

    def test_sequences_are_independent_per_cash_journal(self):
        CashRegister = self.env["l10n.ro.cash.register"]
        year = date.today().year

        # Two registers on journal A (different dates to satisfy unique(date, journal_id))
        a1 = CashRegister.create({"journal_id": self.journal_a.id, "date": date(year, 1, 10)})
        a2 = CashRegister.create({"journal_id": self.journal_a.id, "date": date(year, 1, 15)})
        _logger.info("Cash Register A1: name=%s, prefix=%s, number=%s", a1.name, a1.sequence_prefix, a1.sequence_number)
        _logger.info("Cash Register A2: name=%s, prefix=%s, number=%s", a2.name, a2.sequence_prefix, a2.sequence_number)

        # Two registers on journal B
        b1 = CashRegister.create({"journal_id": self.journal_b.id, "date": date(year, 2, 1)})
        b2 = CashRegister.create({"journal_id": self.journal_b.id, "date": date(year, 2, 10)})
        _logger.info("Cash Register B1: name=%s, prefix=%s, number=%s", b1.name, b1.sequence_prefix, b1.sequence_number)
        _logger.info("Cash Register B2: name=%s, prefix=%s, number=%s", b2.name, b2.sequence_prefix, b2.sequence_number)

        # Assert numbering increments per journal independently
        self.assertEqual(a1.sequence_number, 1, "First register on journal A should start at 1")
        self.assertEqual(a2.sequence_number, 2, "Second register on journal A should be 2")

        self.assertEqual(b1.sequence_number, 1, "First register on journal B should start at 1")
        self.assertEqual(b2.sequence_number, 2, "Second register on journal B should be 2")

        # Assert prefixes are per journal/range and consistent within the same journal
        self.assertEqual(
            a1.sequence_prefix,
            a2.sequence_prefix,
            "Registers on the same journal should share the same prefix/range",
        )
        self.assertEqual(
            b1.sequence_prefix,
            b2.sequence_prefix,
            "Registers on the same journal should share the same prefix/range",
        )
        self.assertNotEqual(
            a1.sequence_prefix,
            b1.sequence_prefix,
            "Different journals must produce different prefix ranges (e.g., CASH vs PETY)",
        )

        # Sanity: names should be properly formatted (prefix + number)
        self.assertTrue(a1.name and a1.name != "/", "Name should be set on creation for a1")
        self.assertTrue(a2.name and a2.name != "/", "Name should be set on creation for a2")
        self.assertTrue(b1.name and b1.name != "/", "Name should be set on creation for b1")
        self.assertTrue(b2.name and b2.name != "/", "Name should be set on creation for b2")

    def test_assign_number_on_write_if_missing(self):
        """On save (write), if the number is missing, it should be assigned automatically."""
        CashRegister = self.env["l10n.ro.cash.register"]
        year = date.today().year

        rec = CashRegister.create({"journal_id": self.journal_a.id, "date": date(year, 3, 1)})
        self.assertTrue(rec.name, "Number should be assigned on create")

        # Simulate user clearing the number; then saving any change should reassign a number
        rec.write({"name": False})
        self.assertFalse(rec.name, "Precondition: name cleared")

        # Write an unrelated field to trigger our write hook
        rec.write({"currency_id": self.env.company.currency_id.id})

        self.assertTrue(rec.name and rec.name != "/", "Number should be (re)assigned on write when missing")

    def test_register_number_does_not_continue_entry_numbering(self):
        """Registrul are contorul lui, chiar în aceeași tranzacție cu notele jurnalului.

        Registrul și notele jurnalului de casă au același format (CASH/2026/00001), iar cheia
        din cache-ul de secvență al `sequence.mixin` este (format, jurnal) — fără un cache
        separat, registrul creat după postarea unei note continua numerotarea notelor.
        """
        year = date.today().year
        counterpart = self.env["account.account"].create(
            {"name": "Counterpart", "code": "1010C", "account_type": "asset_current"}
        )
        moves = self.env["account.move"].create(
            [
                {
                    "move_type": "entry",
                    "journal_id": self.journal_a.id,
                    "date": date(year, 4, day),
                    "line_ids": [
                        (0, 0, {"account_id": self.acc_cash_a.id, "debit": 100.0}),
                        (0, 0, {"account_id": counterpart.id, "credit": 100.0}),
                    ],
                }
                for day in (1, 2)
            ]
        )
        moves.action_post()
        register = self.env["l10n.ro.cash.register"].create({"journal_id": self.journal_a.id, "date": date(year, 4, 2)})
        self.assertEqual(moves.mapped("sequence_number"), [1, 2])
        self.assertEqual(register.sequence_number, 1)
