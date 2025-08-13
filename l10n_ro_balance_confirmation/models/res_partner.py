# ©  2008-now Terrabit <office(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends_context("company", "date_to")
    def _credit_debit_get(self):
        date = self.env.context.get("date_to")
        if not date:
            return super()._credit_debit_get()

        if not self.ids:
            self.debit = False
            self.credit = False
            return
        tables, where_clause, where_params = (
            self.env["account.move.line"]
            ._where_calc(
                [
                    ("parent_state", "=", "posted"),
                    ("company_id", "child_of", self.env.company.root_id.id),
                    ("date", "<=", date),
                ]
            )
            .get_sql()
        )

        where_params = [tuple(self.ids)] + where_params
        if where_clause:
            where_clause = "AND " + where_clause
        self.env["account.move.line"].flush_model(
            [
                "account_id",
                "debit",
                "credit",
                "amount_residual",
                "company_id",
                "parent_state",
                "partner_id",
                "reconciled",
            ]
        )
        self.env["account.account"].flush_model(["account_type"])
        self._cr.execute(
            """
            SELECT account_move_line.partner_id, a.account_type, SUM(account_move_line.debit - account_move_line.credit)
                      FROM """
            + tables
            + """
                      LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                      WHERE a.account_type IN ('asset_receivable','liability_payable')
                      AND account_move_line.partner_id IN %s

                      """
            + where_clause
            + """
                      GROUP BY account_move_line.partner_id, a.account_type
                      """,
            where_params,
        )
        treated = self.browse()
        for pid, acc_type, val in self._cr.fetchall():
            partner = self.browse(pid)
            if acc_type == "asset_receivable":
                partner.credit = val
                if partner not in treated:
                    partner.debit = False
                    treated |= partner
            elif acc_type == "liability_payable":
                partner.debit = -val
                if partner not in treated:
                    partner.credit = False
                    treated |= partner
        remaining = self - treated
        remaining.debit = False
        remaining.credit = False
