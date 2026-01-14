from odoo import fields
from odoo.tests.common import TransactionCase


class TestBalanceConfirmation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.report = cls.env["ir.actions.report"]._get_report_from_name(
            "l10n_ro_balance_confirmation.report_partner_balance"
        )

    def test_report_values_default(self):
        # Test default (today)
        values = self.env["report.l10n_ro_balance_confirmation.report_partner_balance"]._get_report_values(
            self.partner.ids
        )
        self.assertEqual(values["date_to"], fields.Date.today())

    def test_report_values_data(self):
        # Test from data
        date_to = "2025-12-31"
        values = self.env["report.l10n_ro_balance_confirmation.report_partner_balance"]._get_report_values(
            self.partner.ids, data={"date_to": date_to}
        )
        self.assertEqual(values["date_to"], fields.Date.to_date(date_to))

    def test_report_values_context(self):
        # Test from context
        date_to = "2025-11-30"
        values = (
            self.env["report.l10n_ro_balance_confirmation.report_partner_balance"]
            .with_context(date_to=date_to)
            ._get_report_values(self.partner.ids)
        )
        self.assertEqual(values["date_to"], fields.Date.to_date(date_to))

    def test_report_values_param(self):
        # Test from system parameter
        date_to = "2025-10-20"
        self.env["ir.config_parameter"].sudo().set_param("l10n_ro_balance_confirmation.date_to", date_to)
        values = self.env["report.l10n_ro_balance_confirmation.report_partner_balance"]._get_report_values(
            self.partner.ids
        )
        self.assertEqual(values["date_to"], fields.Date.to_date(date_to))
        # cleanup
        self.env["ir.config_parameter"].sudo().set_param("l10n_ro_balance_confirmation.date_to", False)
