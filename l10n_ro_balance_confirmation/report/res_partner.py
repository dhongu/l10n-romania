# ©  2008-now Terrabit <office(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from odoo import api, models


class ReportPartnerBalance(models.AbstractModel):
    _name = "report.l10n_ro_balance_confirmation.report_partner_balance"
    _description = "ReportPartnerBalance"
    _template = "l10n_ro_balance_confirmation.report_partner_balance"

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env["ir.actions.report"]._get_report_from_name(self._template)
        if not docids:
            docids = self.env.context.get("active_ids")
        return {
            "doc_ids": docids,
            "doc_model": report.model,
            "data": data,
            "docs": self.env[report.model].browse(docids),
        }
