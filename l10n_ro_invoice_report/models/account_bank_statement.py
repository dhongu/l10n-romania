# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def button_print(self):
        res = self.env.ref(
            "l10n_ro_invoice_report.action_report_statement_line"
        ).report_action(self)
        return res
