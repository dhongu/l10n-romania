# ©  2008-2022 Terrabit
# See README.rst file on addons root folder for license details


from odoo import models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    def get_debit_credit(self):
        self.ensure_one()
        tables, where_clause, where_params = (
            self.env["account.move.line"].with_context(state="posted", company_id=self.env.company.id)._query_get()
        )
        where_params = [tuple(self.ids)] + where_params
        if where_clause:
            where_clause = "AND " + where_clause
        self._cr.execute(
            """SELECT account_move_line.partner_id, act.type, SUM(account_move_line.amount_residual)
                      FROM """
            + tables
            + """
                      LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                      LEFT JOIN account_account_type act ON (a.user_type_id=act.id)
                      WHERE act.type IN ('receivable','payable')
                      AND account_move_line.partner_id IN %s
                      AND account_move_line.reconciled IS NOT TRUE
                      """
            + where_clause
            + """
                      GROUP BY account_move_line.partner_id, act.type
                      """,
            where_params,
        )
        debit = 0.0
        credit = 0.0
        for type, val in self._cr.fetchall():
            if type == "receivable":
                credit = val
            elif type == "payable":
                debit = -val
        return debit, credit
