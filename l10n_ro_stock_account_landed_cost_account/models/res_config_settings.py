# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ro_landed_cost_intermediary_account_id = fields.Many2one(
        related="company_id.l10n_ro_landed_cost_intermediary_account_id",
        readonly=False,
    )
