# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import importlib.util
from datetime import date

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import SQL
from odoo.tools.misc import file_path


def _load_pre_migration():
    path = file_path("l10n_ro_cash_register/migrations/20.0.1.4.2/pre-migration.py")
    spec = importlib.util.spec_from_file_location("l10n_ro_cash_register_pre_migration_20_0_1_4_2", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@tagged("post_install", "-at_install")
class TestMigrationDuplicateNames(TransactionCase):
    """The pre-migration renames duplicate register numbers so the unique index can be created."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        account = cls.env["account.account"].create({"name": "Cash Dup", "code": "1010D", "account_type": "asset_cash"})
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Cash Journal Dup",
                "code": "CDUP",
                "type": "cash",
                "company_id": cls.env.company.id,
                "default_account_id": account.id,
            }
        )

    def test_duplicate_names_are_renamed(self):
        CashRegister = self.env["l10n.ro.cash.register"]
        first = CashRegister.create({"journal_id": self.journal.id, "date": date(2025, 1, 2)})
        second = CashRegister.create({"journal_id": self.journal.id, "date": date(2025, 1, 4)})
        third = CashRegister.create({"journal_id": self.journal.id, "date": date(2025, 1, 3)})
        other = CashRegister.create({"journal_id": self.journal.id, "date": date(2025, 1, 5)})
        self.env.flush_all()

        # Recreate the state of a database numbered before the unique index existed.
        self.env.cr.execute(SQL("DROP INDEX IF EXISTS l10n_ro_cash_register_unique_name"))
        self.env.cr.execute(
            SQL(
                "UPDATE l10n_ro_cash_register SET name = %s WHERE id IN %s",
                first.name,
                (first.id, second.id, third.id),
            )
        )
        duplicate_name = first.name
        other_name = other.name

        with self.assertLogs("l10n_ro_cash_register_pre_migration_20_0_1_4_2", level="WARNING") as logs:
            _load_pre_migration().migrate(self.env.cr, "20.0.1.4.1")
        self.assertEqual(len(logs.records), 2)

        self.env.invalidate_all()
        self.assertEqual(first.name, duplicate_name, "The oldest register keeps its number")
        self.assertEqual(third.name, f"{duplicate_name}/2025-01-03")
        self.assertEqual(second.name, f"{duplicate_name}/2025-01-04")
        self.assertEqual(other.name, other_name, "Registers without duplicates are not renamed")
