# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import time

from odoo import api, models


class ReportPaymentPrint(models.AbstractModel):
    _name = "report.l10n_ro_invoice_report.report_payment"
    _description = "ReportPaymentPrint"
    _template = "l10n_ro_invoice_report.report_payment"

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env["ir.actions.report"]._get_report_from_name(self._template)
        return {
            "doc_ids": docids,
            "doc_model": report.model,
            "data": data,
            "time": time,
            "docs": self.env[report.model].browse(docids),
        }
