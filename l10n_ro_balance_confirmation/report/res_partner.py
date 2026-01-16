# ©  2008-now Terrabit <office(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from datetime import date

from odoo import api, fields, models


class ReportPartnerBalance(models.AbstractModel):
    _name = "report.l10n_ro_balance_confirmation.report_partner_balance"
    _description = "ReportPartnerBalance"
    _template = "l10n_ro_balance_confirmation.report_partner_balance"

    @api.model
    def _get_report_values(self, docids, data=None):
        if not docids:
            docids = self.env.context.get("active_ids")
        if not data:
            data = {}
        date_to = data.get("date_to") or self.env.context.get("date_to")
        if not date_to:
            date_to = self.env["ir.config_parameter"].sudo().get_param("l10n_ro_balance_confirmation.date_to")

        if not date_to:
            date_to = date(date.today().year - 1, 12, 31)

        if date_to and isinstance(date_to, str):
            date_to = fields.Date.to_date(date_to)

        return {
            "doc_ids": docids,
            "doc_model": "res.partner",
            "data": data,
            "docs": self.env["res.partner"].browse(docids),
            "date_to": date_to,
        }
