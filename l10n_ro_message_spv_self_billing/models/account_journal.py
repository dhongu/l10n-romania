# © 2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_ro_spv_number_from_message = fields.Boolean(
        string="Number from SPV message",
        help="Take the document number from the reference of the matched SPV "
        "message instead of the journal sequence. Meant for a dedicated "
        "self-billing journal: the customer issues the invoice in our name, "
        "so the legal number is the one they allocated, not ours.",
    )
