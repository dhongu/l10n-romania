# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import time

from odoo import api, models

# from odoo.tools.safe_eval import safe_eval


class ReportInvoiceWithPaymentsPrint(models.AbstractModel):
    _name = "report.account.report_invoice_with_payments"
    _description = "ReportInvoiceWithPaymentsPrint"
    _template = "account.report_invoice_with_payments"

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
            "with_discount": self._with_discount,
            "amount_to_text": self._amount_to_text,
            "get_pickings": self._get_pickings,
            "get_discount": self._get_discount(),
        }

    def _amount_to_text(self, amount, currency):
        return currency.amount_to_text(amount)

    # def _convert(self, amount):
    #     # todo: de folosit libraria num2words dupa ce o sa aiba si limba romana
    #     amt_ro = amount_to_text_ro.amount_to_text_ro(amount)
    #     return amt_ro

    def _with_discount(self, invoice):
        res = False
        for line in invoice.invoice_line_ids:
            if line.discount != 0.0:
                res = True
        return res

    def _get_pickings(self, invoice):

        if not self.env["ir.module.module"].sudo().search([("name", "=", "stock"), ("state", "=", "installed")]):
            return False

        pickings = self.env["stock.picking"]
        for line in invoice.invoice_line_ids:
            for sale_line in line.sale_line_ids:
                for move in sale_line.move_ids:
                    if move.picking_id.state == "done":
                        pickings |= move.picking_id
            if line.purchase_line_id:
                for move in line.purchase_line_id.move_ids:
                    if move.picking_id.state == "done":
                        pickings |= move.picking_id
        return pickings

    def _get_discount(self):
        config_parameter = self.env["ir.config_parameter"].sudo().search([("key", "=", "l10n_ro_config.show_discount")])
        return config_parameter.value


class ReportInvoicePrint(ReportInvoiceWithPaymentsPrint):
    _name = "report.account.report_invoice"
    _description = "ReportInvoicePrint"
    _template = "account.report_invoice"
