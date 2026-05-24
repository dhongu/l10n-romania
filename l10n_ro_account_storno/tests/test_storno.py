# © 2025 Terrabit - Dorin Hongu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestL10nRoStorno(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.account_storno = True
        ro_country = cls.env.ref("base.ro")
        if cls.company.account_fiscal_country_id != ro_country:
            cls.company.account_fiscal_country_id = ro_country
            cls.company.flush_recordset()

        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "general"), ("company_id", "=", cls.company.id)], limit=1
        )
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create(
                {
                    "name": "Misc RO",
                    "code": "MRO",
                    "type": "general",
                    "company_id": cls.company.id,
                }
            )

        cls.account_biv = cls.env["account.account"].create(
            {
                "name": "Bivalent Test",
                "code": "699901",
                "account_type": "expense",
                "l10n_ro_usage": "bifunctional",
            }
        )
        cls.account_activ = cls.env["account.account"].create(
            {
                "name": "Activ Test",
                "code": "699902",
                "account_type": "expense",
                "l10n_ro_usage": "activ",
            }
        )
        cls.account_pasiv = cls.env["account.account"].create(
            {
                "name": "Pasiv Test",
                "code": "699903",
                "account_type": "liability_current",
                "l10n_ro_usage": "pasiv",
            }
        )

    def _make_move(self, date="2024-01-15"):
        """Helper: create and post a simple journal entry."""
        move = self.env["account.move"].create(
            {
                "journal_id": self.journal.id,
                "move_type": "entry",
                "date": date,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.account_activ.id,
                            "name": "debit line",
                            "debit": 200.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.account_pasiv.id,
                            "name": "credit line",
                            "debit": 0.0,
                            "credit": 200.0,
                        },
                    ),
                ],
            }
        )
        move.action_post()
        return move

    def _reverse_move(self, move):
        """Helper: create a reversal for a posted move."""
        reversal = (
            self.env["account.move.reversal"]
            .with_context(
                active_model="account.move",
                active_ids=move.ids,
            )
            .create(
                {
                    "reason": "Test reversal",
                    "journal_id": self.journal.id,
                }
            )
        )
        reversal.reverse_moves()
        return self.env["account.move"].search([("reversed_entry_id", "=", move.id)], limit=1)

    def test_account_l10n_ro_usage_field(self):
        """Test that l10n_ro_usage field is correctly set on accounts."""
        self.assertEqual(self.account_biv.l10n_ro_usage, "bifunctional")
        self.assertEqual(self.account_activ.l10n_ro_usage, "activ")
        self.assertEqual(self.account_pasiv.l10n_ro_usage, "pasiv")

    def test_account_l10n_ro_usage_default(self):
        """Test that default l10n_ro_usage is bifunctional."""
        account = self.env["account.account"].create(
            {
                "name": "Default Usage Test",
                "code": "699904",
                "account_type": "expense",
            }
        )
        self.assertEqual(account.l10n_ro_usage, "bifunctional")

    def test_storno_enabled_for_ro_company(self):
        """Test that account_storno is enabled for Romanian company."""
        self.assertTrue(self.company.account_storno)

    def test_storno_is_storno_on_reversal(self):
        """Test that reversed move has is_storno set correctly."""
        move = self._make_move()
        self.assertFalse(move.is_storno)

        reversed_move = self._reverse_move(move)
        self.assertTrue(reversed_move.exists(), "Reversed move should exist")
        self.assertEqual(reversed_move.reversed_entry_id, move)
        # is_storno should be opposite of original
        self.assertNotEqual(reversed_move.is_storno, move.is_storno)

    def test_storno_double_reversal(self):
        """Test that double reversal restores is_storno to original value."""
        move = self._make_move()
        original_is_storno = move.is_storno

        rev1 = self._reverse_move(move)
        self.assertTrue(rev1.exists())

        rev2 = self._reverse_move(rev1)
        self.assertTrue(rev2.exists())
        # Double reversal: is_storno should be back to original
        self.assertEqual(rev2.is_storno, original_is_storno)

    def test_l10n_ro_initialize_accounts(self):
        """Test that _l10n_ro_initialize_accounts sets usage on known account codes."""
        activ_account = self.env["account.account"].create(
            {
                "name": "Test Activ 601",
                "code": "601000",
                "account_type": "expense",
                "l10n_ro_usage": "bifunctional",
            }
        )
        pasiv_account = self.env["account.account"].create(
            {
                "name": "Test Pasiv 401",
                "code": "401100",
                "account_type": "liability_current",
                "l10n_ro_usage": "bifunctional",
            }
        )
        # Set company chart to ro so the hook applies
        self.company.chart_template = "ro"
        self.env["res.company"]._l10n_ro_initialize_accounts()
        self.assertEqual(activ_account.l10n_ro_usage, "activ")
        self.assertEqual(pasiv_account.l10n_ro_usage, "pasiv")
