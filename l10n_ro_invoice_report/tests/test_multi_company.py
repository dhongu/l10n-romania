# © 2025 Terrabit / Deltatech
# Multi-company tests for l10n_ro_invoice_report

from odoo.tests.common import TransactionCase


class TestL10nRoInvoiceReportMultiCompany(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env["res.company"]
        cls.Partner = cls.env["res.partner"]
        cls.PartnerBank = cls.env["res.partner.bank"]
        cls.Move = cls.env["account.move"]
        cls.Account = cls.env["account.account"]

        cls.company_a = cls.env.company
        cls.company_b = cls.Company.create({"name": "Company B"})

        cls.Journal = cls.env["account.journal"]
        cls.journal_b = cls.Journal.with_company(cls.company_b).create(
            {
                "name": "Sale Journal B",
                "code": "SJB",
                "type": "sale",
            }
        )

        cls.partner = cls.Partner.create({"name": "Multi-company Partner"})

        cls.bank_a = cls.PartnerBank.create(
            {
                "acc_number": "BANK_A",
                "partner_id": cls.partner.id,
                "company_id": cls.company_a.id,
            }
        )
        cls.bank_b = cls.PartnerBank.create(
            {
                "acc_number": "BANK_B",
                "partner_id": cls.partner.id,
                "company_id": cls.company_b.id,
            }
        )

    def test_company_dependent_payment_bank_id(self):
        # Set bank A for company A
        self.partner.with_company(self.company_a).payment_bank_id = self.bank_a
        # Set bank B for company B
        self.partner.with_company(self.company_b).payment_bank_id = self.bank_b

        self.assertEqual(self.partner.with_company(self.company_a).payment_bank_id, self.bank_a)
        self.assertEqual(self.partner.with_company(self.company_b).payment_bank_id, self.bank_b)

    def test_invoice_partner_bank_id_multi_company(self):
        # Set bank A for company A
        self.partner.with_company(self.company_a).payment_bank_id = self.bank_a
        # Set bank B for company B
        self.partner.with_company(self.company_b).payment_bank_id = self.bank_b

        income_account_a = self.Account.with_company(self.company_a).search([("account_type", "=", "income")], limit=1)

        if not income_account_a:
            income_account_a = self.Account.with_company(self.company_a).create(
                {
                    "name": "Income A",
                    "code": "701",
                    "account_type": "income",
                }
            )

        # Create invoice in company A
        invoice_a = self.Move.with_company(self.company_a).create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "company_id": self.company_a.id,
                "journal_id": self.env["account.journal"]
                .with_company(self.company_a)
                .search([("type", "=", "sale")], limit=1)
                .id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Line",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": income_account_a.id,
                        },
                    )
                ],
            }
        )
        self.assertEqual(invoice_a.partner_bank_id, self.bank_a)

        # Create invoice in company B
        # We might need to ensure company B has a chart of accounts or at least an income account
        # For the sake of this test, we try to find/create one if needed, but often in tests we reuse.
        # However, account.move create checks company_id.

        income_account_b = self.Account.with_company(self.company_b).create(
            {
                "name": "Income B",
                "code": "701",
                "account_type": "income",
            }
        )

        receivable_account_b = self.Account.with_company(self.company_b).create(
            {
                "name": "Receivable B",
                "code": "4111",
                "account_type": "asset_receivable",
            }
        )
        self.partner.with_company(self.company_b).property_account_receivable_id = receivable_account_b

        invoice_b = self.Move.with_company(self.company_b).create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "company_id": self.company_b.id,
                "journal_id": self.journal_b.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Line",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": income_account_b.id,
                        },
                    )
                ],
            }
        )
        self.assertEqual(invoice_b.partner_bank_id, self.bank_b)
