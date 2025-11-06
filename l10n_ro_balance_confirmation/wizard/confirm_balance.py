# ©  2008-2022 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models
from odoo.exceptions import UserError


class BalanceConfirm(models.TransientModel):
    _name = "l10n_ro.balance_confirm_dialog"
    _description = "Wizard for date input for balance confirmation"

    l10n_ro_balance_date = fields.Date(string="At Date", default=fields.Date.today())

    def action_print_balance(self):
        partners = self.env["res.partner"].browse(self.env.context.get("active_ids"))
        if not partners:
            raise UserError(self.env._("No partners selected for balance confirmation."))
        # self = self.with_context(date_to=self.l10n_ro_balance_date)
        # partners = partners.with_context(date_to=self.l10n_ro_balance_date)
        action = self.env.ref("l10n_ro_balance_confirmation.action_report_partner_balance")
        # Curățăm contextul: eliminăm cheia 'date_to' dacă există
        # Curățăm tot contextul și punem doar ce e necesar
        cleaned_context = {
            "lang": self.env.context.get("lang"),
            "tz": self.env.context.get("tz"),
            "uid": self.env.context.get("uid"),
            "allowed_company_ids": self.env.context.get("allowed_company_ids"),
            "active_model": "res.partner",
            "active_ids": partners.ids,
            "active_id": partners.ids[0] if partners else False,
            "date_to": self.l10n_ro_balance_date,  # acesta este critic!
        }
        # action = action.with_context(date_to=self.l10n_ro_balance_date)
        # pylint: disable=W8121
        return action.with_context(cleaned_context).report_action(
            partners,
            data={
                "date_to": self.l10n_ro_balance_date,
                "doc_ids": partners.ids,
            },
        )
