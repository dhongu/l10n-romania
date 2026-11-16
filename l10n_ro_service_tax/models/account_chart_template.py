# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("ro", "res.company")
    def _get_ro_res_company(self):
        res = super()._get_ro_res_company()
        res[self.env.company.id].update(
            {
                "l10n_ro_account_serv_sale_tax_id": "tvac_21_s",
                "l10n_ro_account_serv_purchase_tax_id": "tvad_21_s",
            }
        )
        return res
