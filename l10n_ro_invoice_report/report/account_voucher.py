# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import time

from odoo import api, models

# from . import amount_to_text_ro


class ReportVoucherPrint(models.AbstractModel):
    _name = "report.l10n_ro_invoice_report.report_voucher"
    _description = "ReportVoucherPrint"
    _template = "l10n_ro_invoice_report.report_voucher"

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env["ir.actions.report"]._get_report_from_name(self._template)
        return {
            "doc_ids": docids,
            "doc_model": report.model,
            "data": data,
            "time": time,
            "docs": self.env[report.model].browse(docids),
            # "convert": self._convert,
        }

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env["report"]
        # report = report_obj._get_report_from_name(self._template)
        docargs = self.get_report_values()
        return report_obj.render(self._template, docargs)

    # def _convert(self, amount):
    #     amt_ro = amount_to_text_ro.amount_to_text_ro(amount)
    #     return amt_ro
