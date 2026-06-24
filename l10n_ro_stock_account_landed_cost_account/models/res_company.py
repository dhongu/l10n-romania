# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ro_landed_cost_intermediary_account_id = fields.Many2one(
        "account.account",
        string="Landed Cost Intermediary Account",
        help="Technical intermediary account used to transfer service costs into "
        "products on landed cost validation (e.g. 482.99). When set, a landed cost "
        "entry that would credit a class 6 (expense) account is routed through this "
        "account, producing two clean balanced notes (stock valuation = intermediary "
        "account and intermediary account = class 6) instead of a direct stock "
        "valuation = class 6 entry. Class 609 is never rerouted. Leave empty to keep "
        "the standard behaviour.",
    )
