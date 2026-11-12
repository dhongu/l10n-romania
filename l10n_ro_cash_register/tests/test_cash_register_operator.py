# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import date

from odoo.exceptions import AccessError, UserError
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
        # Compania de test poate avea altă monedă decât RON/EUR din datele modulului (ex. USD în CI):
        # fără cupiuri pe moneda casei, „Numără numerarul” nu are ce adăuga.
        currency = cls.env.company.currency_id
        if not cls.env["l10n.ro.cash.denomination"].search_count([("currency_id", "=", currency.id)]):
            cls.env["l10n.ro.cash.denomination"].create(
                [
                    {"currency_id": currency.id, "value": value, "kind": "banknote" if value >= 1 else "coin"}
                    for value in (100, 10, 1, 0.1)
                ]
            )
        cls.counterpart = cls.env["account.account"].search(
            [("company_ids", "in", cls.env.company.id), ("account_type", "=", "income")], limit=1
        )

    def _visible(self, user):
        return self.env["l10n.ro.cash.register"].with_user(user).search([("id", "in", self.all_registers.ids)])

    def _operation(self, user, journal, amount=100.0, account=None):
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
                    "counterpart_account_id": (account or self.counterpart).id,
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
        visible = (
            self.env["l10n.ro.cash.register.count.line"].with_user(self.operator).search([("id", "in", lines.ids)])
        )
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

    def test_operator_cannot_use_a_cash_or_bank_account_as_counterpart(self):
        """Fără transfer direct între case: contul corespondent de numerar sau bancă e refuzat."""
        with self.assertRaises(UserError):
            self._operation(self.operator, self.journal_a, account=self.journal_b.default_account_id)

    def test_accountant_can_use_a_cash_account_as_counterpart(self):
        move = self._operation(self.accountant, self.journal_a, account=self.journal_b.default_account_id)
        self.assertEqual(move.state, "posted")

    def test_operator_group_does_not_inherit_an_accounting_group(self):
        """Operatorul poate fi doar utilizator intern (ex. operator POS): fără grup contabil moștenit."""
        self.assertFalse(self.operator.has_group("account.group_account_readonly"))
        self.assertFalse(self.operator.has_group("account.group_account_invoice"))

    def test_operator_has_its_own_menu_and_no_accounting_menu(self):
        visible = self.env["ir.ui.menu"].with_user(self.operator)._visible_menu_ids()
        app = self.env.ref("l10n_ro_cash_register.menu_cash_register_app")
        registers = self.env.ref("l10n_ro_cash_register.menu_cash_register_app_registers")
        self.assertIn(app.id, visible)
        self.assertIn(registers.id, visible)
        self.assertNotIn(self.env.ref("account.menu_finance_entries").id, visible)

    def test_operator_reads_the_lines_of_the_register(self):
        move = self._operation(self.operator, self.journal_a)
        register = self.register_a.with_user(self.operator)
        register.action_refresh()
        self.assertEqual(register.move_ids, move)
        # câmpurile afișate în fila de linii se citesc fără grup contabil
        self.assertEqual(register.move_line_ids.mapped("move_name"), [move.name] * len(register.move_line_ids))
        self.assertTrue(register.move_line_ids.mapped("balance"))

    def test_operator_prints_the_register_and_the_cash_count(self):
        self._operation(self.operator, self.journal_a)
        register = self.register_a.with_user(self.operator)
        register.action_refresh()
        report = self.env["ir.actions.report"].with_user(self.operator)
        html, _fmt = report._render_qweb_html("l10n_ro_cash_register.report_cash_register", register.ids)
        self.assertIn(register.name.encode(), html)
        register.action_count_cash()
        report._render_qweb_html("l10n_ro_cash_register.report_cash_count", register.ids)

    def test_accountant_does_not_get_the_operator_app_menu(self):
        """Contabilul are meniul sub Contabilitate; aplicația separată e doar a operatorilor."""
        app = self.env.ref("l10n_ro_cash_register.menu_cash_register_app")
        classic = self.env.ref("l10n_ro_cash_register.menu_cash_register")
        accountant_menus = self.env["ir.ui.menu"].with_user(self.accountant)._visible_menu_ids()
        self.assertNotIn(app.id, accountant_menus)
        self.assertIn(classic.id, accountant_menus)
        operator_menus = self.env["ir.ui.menu"].with_user(self.operator)._visible_menu_ids()
        self.assertNotIn(classic.id, operator_menus)
        # cine are ambele grupuri vede ambele meniuri
        both_menus = self.env["ir.ui.menu"].with_user(self.both)._visible_menu_ids()
        self.assertIn(app.id, both_menus)
        self.assertIn(classic.id, both_menus)

    def test_operator_group_is_listed_under_a_privilege(self):
        """Fără privilegiu, grupul se vede în fișa utilizatorului doar în modul dezvoltator."""
        self.assertTrue(self.group_operator.privilege_id)

    def test_operator_can_use_the_internal_transfer_account(self):
        """Alimentarea casei din bancă și depunerea la bancă merg prin contul de transfer al companiei."""
        transfer = self.env["account.account"].create(
            {"code": "581999", "name": "Transfer test", "account_type": "asset_cash"}
        )
        self.env.company.transfer_account_id = transfer
        move = self._operation(self.operator, self.journal_a, account=transfer)
        self.assertEqual(move.state, "posted")
        # alt cont de numerar/bancă rămâne refuzat
        with self.assertRaises(UserError):
            self._operation(self.operator, self.journal_a, account=self.journal_b.default_account_id)
