from odoo.tests import common


class TestSearchBalance(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.country_ro = cls.env.ref("base.ro")
        cls.state_b = cls.env["res.country.state"].search([("country_id", "=", cls.country_ro.id)], limit=1)
        cls.partner_a = cls.env["res.partner"].create(
            {
                "name": "Partner A",
                "country_id": cls.country_ro.id,
                "state_id": cls.state_b.id,
                "city": "Bucharest",
                "street": "A Street",
            }
        )
        cls.partner_b = cls.env["res.partner"].create(
            {
                "name": "Partner B",
                "country_id": cls.country_ro.id,
                "state_id": cls.state_b.id,
                "city": "Bucharest",
                "street": "B Street",
            }
        )
        cls.partner_c = cls.env["res.partner"].create(
            {
                "name": "Partner C",
                "country_id": cls.country_ro.id,
                "state_id": cls.state_b.id,
                "city": "Bucharest",
                "street": "C Street",
            }
        )

        cls.account_receivable = cls.env["account.account"].search(
            [
                ("account_type", "=", "asset_receivable"),
            ],
            limit=1,
        )
        cls.account_revenue = cls.env["account.account"].search(
            [
                ("account_type", "=", "income"),
            ],
            limit=1,
        )

        # Move for partner A: Balance 100 on 2025-01-01
        move_a = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_a.id,
                "date": "2025-01-01",
                "invoice_date": "2025-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test line",
                            "quantity": 1,
                            "price_unit": 100,
                            "account_id": cls.account_revenue.id,
                        },
                    )
                ],
            }
        )
        move_a.action_post()

        # Move for partner B: Balance 0.5 (should be ignored by threshold 1)
        move_b = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_b.id,
                "date": "2025-01-01",
                "invoice_date": "2025-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test line",
                            "quantity": 1,
                            "price_unit": 0.5,
                            "account_id": cls.account_revenue.id,
                        },
                    )
                ],
            }
        )
        move_b.action_post()

        # Partner C has no moves.

    def test_search_has_debit_credit_at_date(self):
        # Search at date where A has balance, B has small balance, C has none
        # Date 2025-01-01
        partners = (
            self.env["res.partner"].with_context(date_to="2025-01-01").search([("has_debit_credit_at_date", "=", True)])
        )
        self.assertIn(self.partner_a, partners)
        self.assertNotIn(self.partner_b, partners)
        self.assertNotIn(self.partner_c, partners)

        # Search at date before moves (2024-12-31)
        partners = (
            self.env["res.partner"].with_context(date_to="2024-12-31").search([("has_debit_credit_at_date", "=", True)])
        )
        self.assertNotIn(self.partner_a, partners)
        self.assertNotIn(self.partner_b, partners)
        self.assertNotIn(self.partner_c, partners)

    def test_search_operator_not_true(self):
        # Search for partners NOT having debit/credit
        partners = (
            self.env["res.partner"]
            .with_context(date_to="2025-01-01")
            .search(
                [
                    ("has_debit_credit_at_date", "=", False),
                    ("id", "in", (self.partner_a | self.partner_b | self.partner_c).ids),
                ]
            )
        )
        self.assertNotIn(self.partner_a, partners)
        self.assertIn(self.partner_b, partners)
        self.assertIn(self.partner_c, partners)

    def test_search_with_config_parameter(self):
        # Test using system parameter instead of context
        self.env["ir.config_parameter"].sudo().set_param("l10n_ro_balance_confirmation.date_to", "2025-01-01")
        partners = self.env["res.partner"].search([("has_debit_credit_at_date", "=", True)])
        self.assertIn(self.partner_a, partners)

        # Cleanup
        self.env["ir.config_parameter"].sudo().set_param("l10n_ro_balance_confirmation.date_to", False)
