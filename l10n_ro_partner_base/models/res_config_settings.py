# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ro_vat_nrc_unique = fields.Selection(
        [
            ("off", "Not checked"),
            ("vat", "Unique VAT"),
            ("vat_nrc", "Unique VAT and NRC"),
        ],
        string="Romania - Unique Partners",
        config_parameter="l10n_ro_partner_unique.vat_nrc_unique",
        default="off",
        help="Prevents the creation of two company partners with the same VAT "
        "(or the same VAT and NRC) in a company with the Romanian fiscal country.",
    )
