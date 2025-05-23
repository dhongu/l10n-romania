# ©  2025 Terrabit
# See README.rst file on addons root folder for license details


from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _where_calc(self, domain, active_test=True, options=False):
        date = self.env.context.get("date_to")
        if date:
            domain += [("date", "<=", date)]
        return super()._where_calc(domain, active_test=active_test, options=options)
