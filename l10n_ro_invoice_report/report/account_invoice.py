# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class ReportInvoiceWithoutPayment(models.AbstractModel):
    _inherit = "report.account.report_invoice"

    @api.model
    def _get_report_values(self, docids, data=None):
        result = super()._get_report_values(docids, data)
        result.update(
            {
                "with_discount": self._with_discount,
                "amount_to_text": self._amount_to_text,
                "get_pickings": self._get_pickings,
                "get_discount": self._get_discount(),
            }
        )
        return result

    def _amount_to_text(self, amount, currency):
        return currency.amount_to_text(amount)

    def _with_discount(self, invoice):
        res = False
        for line in invoice.invoice_line_ids:
            if line.discount != 0.0:
                res = True
        return res

    def _get_pickings(self, invoice):
        if (
            not self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", "stock"), ("state", "=", "installed")])
        ):
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
        params = self.env["ir.config_parameter"].sudo()
        show_discount = params.get_param("l10n_ro_config.show_discount", default="True")
        show_discount = safe_eval(show_discount)

        return show_discount


class ReportInvoicePrintInCompanyLanguage(models.AbstractModel):
    _name = "report.l10n_ro_invoice_report.report_invoice_company_language"
    _description = "Report Invoice in Company Language"
    _inherit = "report.account.report_invoice"
    _template = "l10n_ro_invoice_report.report_invoice_company_language"
