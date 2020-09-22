# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ReportPartnerStatement(models.AbstractModel):
    _name = "report.l10n_ro_account_report.report_partner_statement"
    _description = "Partner Statement"
    _template = "l10n_ro_account_report.report_partner_statement"
