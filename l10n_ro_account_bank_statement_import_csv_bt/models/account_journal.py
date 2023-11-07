# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _get_bank_statements_available_import_formats(self):
        rslt = super()._get_bank_statements_available_import_formats()
        rslt.append("CSV")
        return rslt
