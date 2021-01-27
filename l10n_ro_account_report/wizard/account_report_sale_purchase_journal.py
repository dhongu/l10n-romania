# ©  2018 Terrabit
# See README.rst file on addons root folder for license details

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import safe_eval


class SalePurchaseJournalReport(models.TransientModel):
    _name = "account.report.sale.purchase.journal"
    _description = "SalePurchaseJournalReport"

    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.user.company_id
    )

    date_range_id = fields.Many2one("date.range", string="Date range")
    date_from = fields.Date("Start Date", required=True)
    date_to = fields.Date("End Date", required=True)
    journal = fields.Selection([("purchase", "Purchase"), ("sale", "Sale")], string="Journal type", required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(SalePurchaseJournalReport, self).default_get(fields_list)
        today = fields.Date.context_today(self)
        today = fields.Date.from_string(today)

        from_date = today + relativedelta(day=1, months=-1, days=0)
        to_date = today + relativedelta(day=1, months=0, days=-1)

        res["date_from"] = fields.Date.to_string(from_date)
        res["date_to"] = fields.Date.to_string(to_date)
        return res

    @api.multi
    def button_show(self):
        journals = self.env["account.journal"].search(
            [("type", "=", self.journal), ("company_id", "=", self.company_id.id)]
        )
        invoices = self.env["account.invoice"].search(
            [
                ("date_invoice", ">=", self.date_from),
                ("date_invoice", "<=", self.date_to),
                ("journal_id", "in", journals.ids),
                ("company_id", "=", self.company_id.id),
            ],
            order="date_invoice",
        )
        data = {"wizard_id": self.id}
        # data['docids'] = invoices.ids

        report = self.env.ref("l10n_ro_account_report.action_report_sale_purchase_journal")
        res = report.report_action(invoices, data=data)
        return res
