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
