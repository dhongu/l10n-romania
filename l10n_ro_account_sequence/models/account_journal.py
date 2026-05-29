from odoo import api, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _sync_cash_payment_accounts(self):
        for journal in self.filtered(lambda j: j.type == "cash" and j.default_account_id):
            lines = journal.outbound_payment_method_line_ids + journal.inbound_payment_method_line_ids
            for line in lines:
                account_id = line.payment_account_id.id
                if account_id == journal.default_account_id.id:
                    continue
                if account_id:
                    journal._remove_outstanding_account(account_id)
                line.write({"payment_account_id": journal.default_account_id.id})

    @api.model_create_multi
    def create(self, vals_list):
        journals = super().create(vals_list)
        journals._sync_cash_payment_accounts()
        return journals

    def write(self, vals):
        result = super().write(vals)
        if {
            "type",
            "default_account_id",
            "inbound_payment_method_line_ids",
            "outbound_payment_method_line_ids",
            "currency_id",
        } & set(vals):
            self._sync_cash_payment_accounts()
        return result

    def remove_outstanding_accounts(self):
        self._sync_cash_payment_accounts()

    def _remove_outstanding_account(self, account_id):
        param = {"old_account": account_id, "journal_id": self.id, "new_account": self.default_account_id.id}
        sql = (
            """
            UPDATE account_move_line
                SET account_id = %(new_account)s
                WHERE account_id = %(old_account)s
                    AND journal_id = %(journal_id)s
        """
            ""
        )
        self.env.cr.execute(sql, param)
