# Copyright 2024-2025: OCA / Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestL10nRoAccountReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Report = cls.env["ir.actions.report"]
        cls.report_name = "l10n_ro_account_report.report_statement"
        cls.report_model_name = "report.l10n_ro_account_report.report_statement"

    def test_report_action_exists(self):
        # XMLID should be available and point to the correct model/name
        action = self.env.ref("l10n_ro_account_report.action_report_account_statement")
        self.assertEqual(action.model, "account.bank.statement")
        self.assertEqual(action.report_name, self.report_name)
        self.assertEqual(action.report_file, self.report_name)
        self.assertEqual(action.report_type, "qweb-pdf")

    def test_report_model_is_registered(self):
        # The report should be discoverable by name
        report = self.Report._get_report_from_name(self.report_name)
        self.assertTrue(report, "Report not found by name")
        self.assertEqual(report.model, "account.bank.statement")
        # The abstract model should be present in the registry
        report_model = self.env[self.report_model_name]
        self.assertIsNotNone(report_model)

    def test_get_report_values_minimal(self):
        # Calling with empty docids should still return the structure
        report_model = self.env[self.report_model_name]
        values = report_model._get_report_values([], data={})
        # Must contain the standard keys used by qweb reports
        for key in [
            "doc_ids",
            "doc_model",
            "data",
            "time",
            "docs",
            "formatLang",
            "company",
        ]:
            self.assertIn(key, values)
        self.assertEqual(values["doc_ids"], [])
        self.assertEqual(values["doc_model"], "account.bank.statement")
        self.assertEqual(values["data"], {})
        # formatLang should be callable
        self.assertTrue(callable(values["formatLang"]))
