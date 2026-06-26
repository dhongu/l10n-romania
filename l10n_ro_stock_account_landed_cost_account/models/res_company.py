# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ro_landed_cost_method = fields.Selection(
        [
            ("standard", "Standard (credit class 6 directly)"),
            ("intermediary", "Through intermediary account"),
        ],
        string="Landed Cost Class 6 Method",
        default="standard",
        help="How a landed cost entry that would credit a class 6 (expense) "
        "account is generated:\n"
        "- Standard: native Odoo behaviour (stock valuation = class 6);\n"
        "- Through intermediary account: the class 6 credit is routed through a "
        "technical intermediary account, producing two clean balanced notes "
        "(stock valuation = intermediary and intermediary = class 6) that export "
        "correctly to SAGA. Requires the intermediary account below.",
    )

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
