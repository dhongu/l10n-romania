# Copyright (C) 2018 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Account(models.Model):
    _inherit = "account.account"

    l10n_ro_usage = fields.Selection(
        [("bifunctional", "Bifunctional"), ("activ", "Activ"), ("pasiv", "Pasiv")],
        string="Usage",
        help="Usage of the account in the Romanian accounting system",
        default="bifunctional",
    )
