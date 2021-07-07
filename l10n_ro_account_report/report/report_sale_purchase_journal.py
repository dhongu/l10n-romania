# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import time

from odoo import api, models


class ReportReportStatement(models.AbstractModel):
    _name = "report.l10n_ro_account_report.report_sale_purchase_journal"
    _template = "l10n_ro_account_report.report_sale_purchase_journal"
    _description = "Sale Purchase Journal"

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env["ir.actions.report"]._get_report_from_name(self._template)
        if not docids and data and "docids" in data:
            docids = data["docids"]
        return {
            "doc_ids": docids,
            "doc_model": report.model,
            "time": time,
            "wizard": self.env["account.report.sale.purchase.journal"].browse(data["wizard_id"]),
            "docs": self.env[report.model].browse(docids),
        }
