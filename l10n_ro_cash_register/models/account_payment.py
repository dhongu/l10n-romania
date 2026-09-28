from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_post(self):
        res = super().action_post()
        for payment in self:
            if payment.journal_id.type == "cash":
                domain = [("journal_id", "=", payment.journal_id.id), ("date", "=", payment.date)]
                cash_register = self.env["l10n.ro.cash.register"].sudo().search(domain, limit=1)
                if not cash_register:
                    cash_register.create(
                        {
                            "company_id": payment.company_id.id,
                            "currency_id": payment.currency_id.id or payment.company_id.currency_id.id,
                            "journal_id": payment.journal_id.id,
                            "date": payment.date,
                        }
                    )
        return res

    @api.depends("company_id", "partner_id")
    def _compute_journal_id(self):
        """
        Skip journal compute if called from cash register action
        """
        if not self.env.context.get("keep_journal"):
            return super()._compute_journal_id()
