# Copyright 2024-2025: OCA / Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestL10nRoBalanceConfirmation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Report = cls.env["ir.actions.report"]
        cls.report_name = "l10n_ro_balance_confirmation.report_partner_balance"
        cls.report_model_name = "report.l10n_ro_balance_confirmation.report_partner_balance"
        cls.action_xmlid = "l10n_ro_balance_confirmation.action_report_partner_balance"

    def test_report_action_exists(self):
        # The XMLID should resolve and point to the proper model/name
        action = self.env.ref(self.action_xmlid)
        self.assertEqual(action.model, "res.partner")
        self.assertEqual(action.report_name, self.report_name)
        self.assertEqual(action.report_file, self.report_name)
        # report_type may be defaulted by Odoo, so we don't assert it strictly here.

    def test_report_model_is_registered(self):
        # The report should be discoverable by its technical name
        report = self.Report._get_report_from_name(self.report_name)
        self.assertTrue(report, "Report not found by name")
        self.assertEqual(report.model, "res.partner")
        # The abstract model should be present in the registry
        report_model = self.env[self.report_model_name]
        self.assertIsNotNone(report_model)

    def test_get_report_values_minimal(self):
        # Call with empty docids and empty active_ids to exercise the minimal path
        report_model = self.env[self.report_model_name].with_context(active_ids=[])
        values = report_model._get_report_values([], data={})
        # Must contain the keys defined by the report implementation
        for key in ["doc_ids", "doc_model", "data", "docs", "date_to"]:
            self.assertIn(key, values)
        self.assertEqual(values["doc_ids"], [])
        self.assertEqual(values["doc_model"], "res.partner")
        self.assertEqual(values["data"], {})
        # docs should be a recordset of res.partner (empty here)
        self.assertTrue(hasattr(values["docs"], "_name"))
        self.assertEqual(values["docs"]._name, "res.partner")
        # date_to should be set (string or date), we just check it's truthy
        self.assertTrue(values["date_to"])
