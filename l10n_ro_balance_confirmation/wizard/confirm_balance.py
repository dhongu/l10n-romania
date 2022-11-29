# ©  2008-2022 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models

# from odoo.exceptions import UserError


class BalanceConfirm(models.TransientModel):
    _name = "l10n_ro.balance_confirm_dialog"
    _description = "Wizard for date input for balance confirmation"

    l10n_ro_balance_date = fields.Date(string="Balance confirmation at")

    def action_print_balance(self):
        partners = self.env["res.partner"].browse(self.env.context.get("active_ids"))
        if partners:
            self = self.with_context(date_to=self.l10n_ro_balance_date)
            partners = partners.with_context(date_to=self.l10n_ro_balance_date)
            action = self.env.ref("l10n_ro_balance_confirmation.action_report_partner_balance")
            action = action.with_context(date_to=self.l10n_ro_balance_date)
            return action.report_action(partners, data={"date_to": self.l10n_ro_balance_date})
