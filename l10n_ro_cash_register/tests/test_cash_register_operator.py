# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import date

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestL10nRoCashRegisterOperator(TransactionCase):
    """Operatorul de casă lucrează doar pe casele alocate lui; contabilul vede tot."""

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.chart_template = "ro"
        cls.group_operator = cls.env.ref("l10n_ro_cash_register.group_cash_register_operator")
        cls.group_manager = cls.env.ref("account.group_account_manager")
        users = cls.env["res.users"].with_context(no_reset_password=True)

        def _user(login, groups):
            return users.create(
                {
                    "name": login,
                    "login": login,
                    "email": f"{login}@example.com",
                    "group_ids": [(6, 0, [g.id for g in groups])],
                }
            )

        cls.operator = _user("cash_operator_1", cls.group_operator)
        cls.other_operator = _user("cash_operator_2", cls.group_operator)
        cls.accountant = _user("cash_accountant", cls.group_manager)
        cls.both = _user("cash_operator_accountant", cls.group_operator + cls.group_manager)

        journal = cls.env["account.journal"]
        cls.journal_a = journal.create({"name": "Cash A", "code": "TCA", "type": "cash"})
        cls.journal_b = journal.create({"name": "Cash B", "code": "TCB", "type": "cash"})
        cls.journal_empty = journal.create({"name": "Cash General", "code": "TCG", "type": "cash"})
        cls.journal_a.l10n_ro_cash_operator_ids = cls.operator
        cls.journal_b.l10n_ro_cash_operator_ids = cls.other_operator

        register = cls.env["l10n.ro.cash.register"]
        cls.register_a = register.create({"journal_id": cls.journal_a.id, "date": date(2026, 3, 2)})
        cls.register_b = register.create({"journal_id": cls.journal_b.id, "date": date(2026, 3, 2)})
        cls.register_empty = register.create({"journal_id": cls.journal_empty.id, "date": date(2026, 3, 2)})
        cls.all_registers = cls.register_a | cls.register_b | cls.register_empty
        cls.counterpart = cls.env["account.account"].search(
            [("company_ids", "in", cls.env.company.id), ("account_type", "=", "income")], limit=1
        )

    def _visible(self, user):
        return self.env["l10n.ro.cash.register"].with_user(user).search([("id", "in", self.all_registers.ids)])

    def _operation(self, user, journal, amount=100.0):
        wizard = (
            self.env["l10n.ro.cash.register.operation"]
            .with_user(user)
            .create(
                {
                    "journal_id": journal.id,
                    "date": date(2026, 3, 2),
                    "amount": amount,
                    "operation": "in",
                    "description": "Test operation",
                    "counterpart_account_id": self.counterpart.id,
                }
            )
        )
        wizard.action_confirm()
        return self.env["account.move"].search([("journal_id", "=", journal.id), ("ref", "=", "Test operation")])

    def test_operator_sees_only_own_cash_desk(self):
        self.assertEqual(self._visible(self.operator), self.register_a)
        self.assertEqual(self._visible(self.other_operator), self.register_b)

    def test_empty_operator_list_hides_the_cash_desk_from_operators(self):
        self.assertNotIn(self.register_empty, self._visible(self.operator))
        self.assertNotIn(self.register_empty, self._visible(self.other_operator))

    def test_accountant_sees_everything(self):
        self.assertEqual(self._visible(self.accountant), self.all_registers)

    def test_operator_and_accountant_sees_everything(self):
        """Regula operatorului nu îl restrânge pe contabilul care are și grupul de operator."""
        self.assertEqual(self._visible(self.both), self.all_registers)

    def test_count_lines_follow_the_cash_desk(self):
        denomination = self.env["l10n.ro.cash.denomination"].search([], limit=1)
        lines = self.env["l10n.ro.cash.register.count.line"].create(
            [
                {"register_id": self.register_a.id, "denomination_id": denomination.id},
                {"register_id": self.register_b.id, "denomination_id": denomination.id},
            ]
        )
        visible = self.env["l10n.ro.cash.register.count.line"].with_user(self.operator).search([("id", "in", lines.ids)])
        self.assertEqual(visible.register_id, self.register_a)

    def test_operator_can_close_own_register(self):
        self.register_a.with_user(self.operator).action_close()
        self.assertEqual(self.register_a.state, "closed")
        self.assertEqual(self.register_a.closed_by_id, self.operator)

    def test_operator_cannot_touch_other_cash_desk(self):
        with self.assertRaises(AccessError):
            self.register_b.with_user(self.operator).action_close()

    def test_operator_cannot_reopen_a_closed_day(self):
        self.register_a.with_user(self.operator).action_close()
        with self.assertRaises(AccessError):
            self.register_a.with_user(self.operator).action_reopen()
        with self.assertRaises(AccessError):
            self.register_a.with_user(self.operator).write({"state": "open"})
        self.assertEqual(self.register_a.state, "closed")

    def test_accountant_can_reopen_a_closed_day(self):
        self.register_a.with_user(self.operator).action_close()
        self.register_a.with_user(self.accountant).action_reopen()
        self.assertEqual(self.register_a.state, "open")

    def test_operator_cannot_delete_a_register(self):
        with self.assertRaises(AccessError):
            self.register_a.with_user(self.operator).unlink()

    def test_operator_operation_on_own_cash_desk(self):
        move = self._operation(self.operator, self.journal_a)
        self.assertEqual(move.state, "posted")
        self.assertEqual(move.create_uid, self.operator)

    def test_operator_operation_on_other_cash_desk_is_refused(self):
        with self.assertRaises(AccessError):
            self._operation(self.operator, self.journal_b)
        with self.assertRaises(AccessError):
            self._operation(self.operator, self.journal_empty)

    def test_accountant_operation_on_any_cash_desk(self):
        self.assertEqual(self._operation(self.accountant, self.journal_b).state, "posted")
        self.assertEqual(self._operation(self.both, self.journal_empty).state, "posted")

    def test_operator_cannot_edit_the_operator_list(self):
        with self.assertRaises(AccessError):
            self.journal_a.with_user(self.operator).write({"l10n_ro_cash_operator_ids": [(5, 0, 0)]})
