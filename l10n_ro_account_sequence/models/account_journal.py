from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def remove_outstanding_accounts(self):
        for journal in self:
            if journal.type != "cash":
                continue
            lines = self.outbound_payment_method_line_ids + self.inbound_payment_method_line_ids
            for line in lines:
                account_id = line.payment_account_id.id
                if account_id == journal.default_account_id.id:
                    continue
                if account_id:
                    journal._remove_outstanding_account(account_id)
                line.write({"payment_account_id": journal.default_account_id.id})

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
