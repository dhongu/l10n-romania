from odoo import models


class account_journal(models.Model):
    _inherit = "account.journal"

    def open_action_with_context(self):
        if self.type == "cash" and self.company_id.country_id.code == "RO":
            action = self.env["ir.actions.actions"]._for_xml_id(
                "l10n_ro_cash_register.action_cash_register"
            )
            action["context"] = {"default_journal_id": self.id}
            return action

    def open_action(self):
        if self.type == "cash" and self.company_id.country_id.code == "RO":
            action = self.env["ir.actions.actions"]._for_xml_id(
                "l10n_ro_cash_register.action_cash_register"
            )
            action["context"] = {"default_journal_id": self.id}
            return action
        return super(account_journal, self).open_action()
