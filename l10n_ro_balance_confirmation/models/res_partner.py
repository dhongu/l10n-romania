# ©  2008-now Terrabit <office(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _credit_debit_get(self):
        if not self.env.context.get("date_to"):
            return super()._credit_debit_get()
        else:
            # cautat prin codul sursa si am gasit versiunea asta
            domain = [
                ("parent_state", "=", "posted"),
                ("company_id", "=", self.env.company.id),
            ]
            query = self.env["account.move.line"]._where_calc(domain)
            tables, where_clause, where_params = query.get_sql()
            where_params = [tuple(self.ids)] + where_params

            if where_clause:
                where_clause = "AND " + where_clause

            # am modificat dupa cum o zis dorin si ce am mai cautat eu prin cod
            self._cr.execute(
                f"""
                SELECT account_move_line.partner_id, a.account_type,
                       SUM(account_move_line.debit - account_move_line.credit)
                FROM {tables}
                LEFT JOIN account_account a ON (account_move_line.account_id = a.id)
                WHERE a.account_type IN ('asset_receivable', 'liability_payable')
                AND account_move_line.partner_id IN %s
                {where_clause}
                GROUP BY account_move_line.partner_id, a.account_type
                """,
                where_params,
            )

            treated = self.browse()
            for pid, account_type, val in self._cr.fetchall():
                partner = self.browse(pid)
                if account_type == "asset_receivable":
                    partner.credit = val
                    if partner not in treated:
                        partner.debit = False
                        treated |= partner
                elif account_type == "liability_payable":
                    partner.debit = -val
                    if partner not in treated:
                        partner.credit = False
                        treated |= partner
            remaining = self - treated
            remaining.debit = False
            remaining.credit = False
