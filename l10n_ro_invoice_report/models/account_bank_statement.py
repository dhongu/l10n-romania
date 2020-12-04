from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.multi
    def button_print(self):
        res = self.env.ref("l10n_ro_invoice_report.action_report_statement_line").report_action(self)
        return res
