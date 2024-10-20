from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def print_cash_operation(self):
        pass
