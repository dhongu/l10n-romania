# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ActivityStatementWizard(models.TransientModel):
    """Activity Statement wizard."""

    _name = "l10n_ro.activity.statement.wizard"
    _description = "Activity Statement Wizard"

    def _get_company(self):
        return (
            self.env["res.company"].browse(self.env.context.get("force_company"))
            or self.env.user.company_id
        )

    @api.model
    def _get_date_start(self):
        return fields.Date.context_today(self).replace(day=1, month=1)

    def _get_account_type(self):
        account_type = "payable"
        if self.env.context.get("active_model") == "res.partner":
            partner = self.env["res.partner"].browse(self.env.context["active_id"])
            if partner.customer_rank > 0:
                account_type = "receivable"
        return account_type

    date_range_id = fields.Many2one(comodel_name="date.range", string="Date range")

    name = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=_get_company,
        string="Company",
        required=True,
    )
    date_start = fields.Date(required=True, default=_get_date_start)
    date_end = fields.Date(required=True, default=fields.Date.context_today)

    number_partner_ids = fields.Integer(
        default=lambda self: len(self._context["active_ids"])
    )
    filter_partners_non_due = fields.Boolean(
        string="Don't show partners with no due entries", default=True
    )
    filter_negative_balances = fields.Boolean("Exclude Negative Balances", default=True)

    col_credit_debit = fields.Boolean("Show colums Debit Credit")
    account_type = fields.Selection(
        [("receivable", "Receivable"), ("payable", "Payable")],
        string="Account type",
        default=_get_account_type,
    )

    target_move = fields.Selection(
        [("posted", "All Posted Entries"), ("all", "All Entries")],
        string="Target Moves",
        required=True,
        default="posted",
    )

    @api.onchange("date_range_id")
    def onchange_date_range_id(self):
        """Handle date range change."""
        if self.date_range_id:
            self.date_start = self.date_range_id.date_start
            self.date_end = self.date_range_id.date_end

    def _export(self):
        """Export to PDF."""
        data = self._prepare_statement()
        report = self.env.ref("l10n_ro_account_report.action_print_activity_statement")
        return report.with_context(from_transient_model=True).report_action(
            self, data=data
        )

    def button_show(self):
        self.ensure_one()
        return self._export()

    def _prepare_statement(self):
        self.ensure_one()
        return {
            "date_start": self.date_start,
            "date_end": self.date_end,
            "company_id": self.company_id.id,
            "partner_ids": self._context["active_ids"],
            # 'show_aging_buckets': self.show_aging_buckets,
            "filter_non_due_partners": self.filter_partners_non_due,
            "account_type": self.account_type,
            # 'aging_type': self.aging_type,
            "filter_negative_balances": self.filter_negative_balances,
            "target_move": self.target_move,
        }
