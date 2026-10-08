# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import date

from odoo.exceptions import UserError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestL10nRoCashRegisterCount(TransactionCase):
    """Monetarul: numărarea pe cupiuri comparată cu soldul contului casei."""

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.chart_template = "ro"
        cls.env.ref("base.RON").active = True
        cls.cash_journal = cls.env["account.journal"].create(
            {"name": "Test Cash Count", "code": "TCCN", "type": "cash"}
        )
        cls.cash_account = cls.cash_journal.default_account_id
        cls.counterpart = cls.env["account.account"].search(
            [("company_ids", "in", cls.env.company.id), ("account_type", "=", "income")], limit=1
        )
        cls.profit_account = cls.env["account.account"].search(
            [("company_ids", "in", cls.env.company.id), ("account_type", "in", ("income", "income_other"))],
            limit=1,
        )
        cls.loss_account = cls.env["account.account"].search(
            [("company_ids", "in", cls.env.company.id), ("account_type", "=", "expense")], limit=1
        )
        cls.cash_journal.write({"profit_account_id": cls.profit_account.id, "loss_account_id": cls.loss_account.id})
        cls.day = date(2026, 3, 2)
        # Compania de test poate avea altă monedă decât RON/EUR din datele modulului.
        currency = cls.env.company.currency_id
        denomination = cls.env["l10n.ro.cash.denomination"]
        existing = denomination.search([("currency_id", "=", currency.id)]).mapped("value")
        denomination.create(
            [
                {"currency_id": currency.id, "value": value, "kind": "banknote" if value >= 1 else "coin"}
                for value in (500, 200, 100, 50, 20, 10, 5, 1, 0.5, 0.1, 0.05, 0.01)
                if value not in existing
            ]
        )

    def _cash_move(self, amount):
        move = self.env["account.move"].create(
            {
                "journal_id": self.cash_journal.id,
                "date": self.day,
                "ref": "Test",
                "line_ids": [
                    (0, 0, {"account_id": self.cash_account.id, "debit": amount, "name": "Test"}),
                    (0, 0, {"account_id": self.counterpart.id, "credit": amount, "name": "Test"}),
                ],
            }
        )
        move.action_post()
        return move

    def _register(self):
        register = self.env["l10n.ro.cash.register"].search(
            [("journal_id", "=", self.cash_journal.id), ("date", "=", self.day)]
        )
        return register or self.env["l10n.ro.cash.register"].create(
            {"journal_id": self.cash_journal.id, "date": self.day}
        )

    def _count(self, register, quantities):
        register.action_count_cash()
        for line in register.count_line_ids:
            line.quantity = quantities.get(line.value, 0)

    def test_count_cash_adds_denominations_of_register_currency(self):
        register = self._register()
        register.action_count_cash()
        currency = register._get_count_currency()
        self.assertTrue(register.is_counted)
        self.assertEqual(register.count_line_ids.denomination_id.currency_id, currency)
        self.assertEqual(
            len(register.count_line_ids),
            self.env["l10n.ro.cash.denomination"].search_count([("currency_id", "=", currency.id)]),
        )
        # A doua apăsare nu dublează rândurile.
        register.action_count_cash()
        self.assertEqual(len(register.count_line_ids), len(register.count_line_ids.denomination_id))

    def test_counted_amount_and_difference(self):
        self._cash_move(735.55)
        register = self._register()
        self._count(register, {500: 1, 200: 1, 10: 3, 5: 1, 0.5: 1, 0.05: 1})
        self.assertAlmostEqual(register.counted_amount, 735.55)
        self.assertAlmostEqual(register.count_difference, 0.0)
        register.count_line_ids.filtered(lambda line: line.value == 0.05).quantity = 0
        self.assertAlmostEqual(register.count_difference, -0.05)

    def test_record_difference_prefills_operation(self):
        self._cash_move(100.0)
        register = self._register()
        self._count(register, {100: 1, 1: 2})
        action = register.action_record_difference()
        wizard = Form(self.env[action["res_model"]].with_context(**action["context"]))
        self.assertEqual(wizard.operation, "in")
        self.assertEqual(wizard.amount, 2.0)
        self.assertEqual(wizard.counterpart_account_id, self.profit_account)
        wizard.save().action_confirm()
        register.action_refresh()
        self.assertAlmostEqual(register.balance_end, 102.0)
        self.assertAlmostEqual(register.count_difference, 0.0)

    def test_record_shortage_uses_loss_account(self):
        self._cash_move(100.0)
        register = self._register()
        self._count(register, {50: 1, 20: 2})
        action = register.action_record_difference()
        self.assertEqual(action["context"]["default_operation"], "out")
        self.assertEqual(action["context"]["default_amount"], 10.0)
        self.assertEqual(action["context"]["default_counterpart_account_id"], self.loss_account.id)

    def test_required_count_blocks_closing(self):
        self.cash_journal.l10n_ro_require_cash_count = True
        self._cash_move(100.0)
        register = self._register()
        with self.assertRaises(UserError):
            register.action_close()
        self._count(register, {50: 1})
        with self.assertRaises(UserError):
            register.action_close()
        self._count(register, {100: 1})
        register.action_close()
        self.assertEqual(register.state, "closed")

    def test_closing_without_requirement_ignores_count(self):
        self._cash_move(100.0)
        register = self._register()
        register.action_close()
        self.assertEqual(register.state, "closed")

    def test_closed_count_is_locked(self):
        self._cash_move(100.0)
        register = self._register()
        self._count(register, {100: 1})
        register.action_close()
        with self.assertRaises(UserError):
            register.count_line_ids[0].quantity = 5
        with self.assertRaises(UserError):
            register.action_count_cash()
        register.action_reopen()
        register.count_line_ids[0].quantity = 0

    def test_print_cash_count(self):
        self._cash_move(100.0)
        register = self._register()
        with self.assertRaises(UserError):
            register.action_print_cash_count()
        self._count(register, {100: 1})
        html = self.env["ir.actions.report"]._render_qweb_html("l10n_ro_cash_register.report_cash_count", register.ids)[
            0
        ]
        self.assertIn(b"Cash Count by Denomination", html)


@tagged("post_install", "-at_install")
class TestL10nRoCashRegisterCountRoChart(AccountTestInvoicingCommon):
    """Pe planul RO, fără conturi pe jurnal, diferența merge pe 7588/65882, nu pe conturile
    999xxx de diferențe de numerar create de Odoo pentru companie."""

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        day = date(2026, 3, 2)
        cls.cash_journal = cls.env["account.journal"].create({"name": "Test Cash RO", "code": "TCRO", "type": "cash"})
        cls.cash_journal.write({"profit_account_id": False, "loss_account_id": False})
        move = cls.env["account.move"].create(
            {
                "journal_id": cls.cash_journal.id,
                "date": day,
                "line_ids": [
                    (0, 0, {"account_id": cls.cash_journal.default_account_id.id, "debit": 10.0, "name": "Test"}),
                    (
                        0,
                        0,
                        {"account_id": cls.company_data["default_account_revenue"].id, "credit": 10.0, "name": "Test"},
                    ),
                ],
            }
        )
        move.action_post()
        register = cls.env["l10n.ro.cash.register"]
        cls.register = register.search(
            [("journal_id", "=", cls.cash_journal.id), ("date", "=", day)]
        ) or register.create({"journal_id": cls.cash_journal.id, "date": day})
        cls.register.action_count_cash()

    def _set_counted(self, value):
        self.register.count_line_ids.quantity = 0
        self.register.count_line_ids.filtered(lambda line: line.value == value).quantity = 1

    def test_surplus_defaults_to_7588(self):
        self._set_counted(20)
        self.assertGreater(self.register.count_difference, 0)
        self.assertTrue(self.register._get_count_difference_account().code.startswith("7588"))

    def test_shortage_defaults_to_65882(self):
        self._set_counted(5)
        self.assertLess(self.register.count_difference, 0)
        self.assertTrue(self.register._get_count_difference_account().code.startswith("65882"))
