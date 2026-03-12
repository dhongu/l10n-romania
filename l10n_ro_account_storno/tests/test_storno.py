# © 2025 Terrabit - Dorin Hongu
from odoo.tests.common import TransactionCase


class TestL10nRoStorno(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.account_storno = True

        # Set company to Romania so that account_storno is enabled by core compute
        ro_country = cls.env.ref("base.ro")
        if cls.company.account_fiscal_country_id != ro_country:
            cls.company.account_fiscal_country_id = ro_country
            cls.company.flush_recordset()

        # Journal
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Misc RO",
                "code": "MRO",
                "type": "general",
                "company_id": cls.company.id,
            }
        )

        # Accounts
        cls.account_biv = cls.env["account.account"].create(
            {
                "name": "Bivalent",
                "code": "601000",
                "account_type": "expense",
                "l10n_ro_usage": "bifunctional",
            }
        )
        cls.account_debit = cls.env["account.account"].create(
            {
                "name": "Debit Only",
                "code": "602000",
                "account_type": "expense",
                "l10n_ro_usage": "activ",
            }
        )
        cls.account_credit = cls.env["account.account"].create(
            {
                "name": "Credit Only",
                "code": "603000",
                "account_type": "liability_current",
                "l10n_ro_usage": "pasiv",
            }
        )

    def test_storno_basic_bivalent(self):
        self.assertTrue(self.company.account_storno, "Storno should be enabled for RO company")

        move = self.env["account.move"].create(
            {
                "journal_id": self.journal.id,
                "move_type": "entry",
                "date": "2023-01-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.account_biv.id,
                            "name": "storno debit",
                            "balance": 100.0,
                            "storno_line": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.account_biv.id,
                            "name": "counter",
                            "balance": -100.0,
                            "storno_line": True,
                        },
                    ),
                ],
            }
        )

        # Create a balanced move with one storno line (initially debit positive)

        line1 = move.line_ids[0]

        # With storno and positive balance (=100), debit becomes -100, credit stays 0
        self.assertEqual(line1.debit, -100.0)
        self.assertEqual(line1.credit, 0.0)
