# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_ro_require_cash_count = fields.Boolean(
        string="Cash Count Required at Closing",
        help="The day of this cash desk can be closed only after the cash is counted by denomination "
        "and the counted amount equals the balance of the cash account.",
    )
