# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ro_landed_cost_method = fields.Selection(
        related="company_id.l10n_ro_landed_cost_method",
        readonly=False,
    )

    l10n_ro_landed_cost_intermediary_account_id = fields.Many2one(
        related="company_id.l10n_ro_landed_cost_intermediary_account_id",
        readonly=False,
    )

    @api.onchange("l10n_ro_landed_cost_method")
    def _onchange_l10n_ro_landed_cost_method_storno(self):
        if self.l10n_ro_landed_cost_method == "intermediary" and not self.account_storno:
            return {
                "warning": {
                    "title": self.env._("Storno accounting is off"),
                    "message": self.env._(
                        "The intermediary account method needs Storno accounting. Enable it in the "
                        "Accounting settings, otherwise the second pair of the landed cost note "
                        "(class 6 and intermediary account) is not posted in red."
                    ),
                }
            }
