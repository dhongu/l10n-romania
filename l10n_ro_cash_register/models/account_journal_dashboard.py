from odoo import models


class account_journal(models.Model):
    _inherit = "account.journal"

    # def open_action_with_context(self):
    #     if self.type == "cash" and self.company_id.country_id.code == "RO":
    #         action = self.env["ir.actions.actions"]._for_xml_id("l10n_ro_cash_register.action_cash_register")
    #         action["context"] = {"default_journal_id": self.id}
    #         return action

    def open_action(self):
        if self.type == "cash" and self.company_id.country_id.code == "RO":
            action = self.env["ir.actions.actions"]._for_xml_id("l10n_ro_cash_register.action_cash_register")
            action["context"] = {"default_journal_id": self.id}
            return action
        return super().open_action()

    def generate_missing_cash_register(self):
        """Generate missing cash registers for all cash journals and for all moves"""

        for journal in self:
            if journal.type != "cash":
                continue

            param = {
                "account_id": journal.default_account_id.id,
                "company_id": journal.company_id.id,
            }
            # cautam toate miscari pentru contul de casa grupate dupa data
            sql = """
                SELECT account_move_line.date
                FROM account_move_line join account_move on account_move_line.move_id = account_move.id
                WHERE account_id = %(account_id)s
                    AND account_move.state = 'posted'
                    AND account_move_line.company_id = %(company_id)s
                GROUP BY account_move_line.date
                ORDER BY account_move_line.date

            """

            self.env.cr.execute(sql, param)
            for row in self.env.cr.dictfetchall():
                date = row["date"]
                # verificam daca exista deja un registru de casa pentru aceasta data
                cash_register = self.env["l10n.ro.cash.register"].search(
                    [("journal_id", "=", journal.id), ("date", "=", date)]
                )
                if not cash_register:
                    cash_register.create(
                        {
                            "company_id": journal.company_id.id,
                            "currency_id": journal.currency_id.id,
                            "journal_id": journal.id,
                            "date": date,
                        }
                    )
        return True

    def remove_outstanding_accounts(self):
        for journal in self:
            if journal.type != "cash":
                continue
            lines = self.outbound_payment_method_line_ids + self.inbound_payment_method_line_ids
            for line in lines:
                account_id = line.payment_account_id.id or self.company_id.account_journal_payment_debit_account_id.id
                if account_id == journal.default_account_id.id:
                    continue
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
