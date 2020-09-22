# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import time

from odoo import api, models

# from . import amount_to_text_ro


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
            # "convert": self._convert,
        }

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env["report"]
        # report = report_obj._get_report_from_name(self._template)
        docargs = self.get_report_values()
        return report_obj.render(self._template, docargs)

    # def _convert(self, amount):
    #     # de folosit  num2words
    #     amt_ro = amount_to_text_ro.amount_to_text_ro(abs(amount))
    #     return amt_ro


class ReportStatementLinePrint(models.AbstractModel):
    _name = "report.l10n_ro_invoice_report.report_statement_line"
    _description = "ReportStatementLinePrint"
    _template = "l10n_ro_invoice_report.report_statement_line"

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
    #     amt_ro = amount_to_text_ro.amount_to_text_ro(abs(amount))
    #     return amt_ro


class ReportStatementLineVoucher(ReportStatementLinePrint):
    _name = "report.l10n_ro_invoice_report.report_statement_voucher"
    _description = "ReportStatementLineVoucher"
    _template = "l10n_ro_invoice_report.report_statement_voucher"


class ReportStatementLinePayment(ReportStatementLinePrint):
    _name = "report.l10n_ro_invoice_report.report_statement_payment"
    _description = "ReportStatementLinePayment"
    _template = "l10n_ro_invoice_report.report_statement_payment"


class ReportStatementLineCollection(ReportStatementLinePrint):
    _name = "report.l10n_ro_invoice_report.report_statement_collection"
    _description = "ReportStatementLineCollection"
    _template = "l10n_ro_invoice_report.report_statement_collection"
