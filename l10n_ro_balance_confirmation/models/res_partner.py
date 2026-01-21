# ©  2008-now Terrabit <office(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from datetime import date

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    has_debit_credit_at_date = fields.Boolean(
        "Cu sold la 31 dec.", compute="_compute_credit_debit_date", search="_search_credit_debit_date"
    )

    @api.depends_context("date_to")
    def _compute_credit_debit_date(self):
        for partner in self:
            partner._credit_debit_get()
            partner.has_debit_credit_at_date = abs(partner.debit) > 1 or abs(partner.credit) > 1

    def _search_credit_debit_date(self, operator, value):
        if operator not in ("=", "!=") or not isinstance(value, bool):
            raise NotImplementedError("Only = and != operators with boolean values are supported")

        date_to = self.env["ir.config_parameter"].sudo().get_param("l10n_ro_balance_confirmation.date_to")
        if not date_to:
            date_to = date(date.today().year - 1, 12, 31)
        elif isinstance(date_to, str):
            date_to = fields.Date.to_date(date_to)

        date_to_search = self.env.context.get("date_to") or date_to

        query = self.env["account.move.line"]._where_calc(
            [
                ("parent_state", "=", "posted"),
                ("company_id", "child_of", self.env.company.root_id.id),
                ("date", "<=", date_to_search),
                ("account_id.account_type", "in", ("asset_receivable", "liability_payable")),
            ]
        )
        self.env["account.move.line"].flush_model(
            ["account_id", "amount_residual", "company_id", "parent_state", "partner_id", "reconciled"]
        )
        self.env["account.account"].flush_model(["account_type"])

        tables, where_clause, where_params = query.get_sql()

        sql = """
            SELECT account_move_line.partner_id
            FROM {}
            LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
            WHERE a.account_type IN ('asset_receivable','liability_payable')
            AND {}
            GROUP BY account_move_line.partner_id
            HAVING ABS(SUM(
                CASE
                    WHEN a.account_type = 'asset_receivable' THEN account_move_line.debit - account_move_line.credit
                    ELSE account_move_line.credit - account_move_line.debit
                END
            )) > 1
        """.format(tables, where_clause or "TRUE")

        self._cr.execute(sql, where_params)
        res = self._cr.fetchall()
        partner_ids = [r[0] for r in res]

        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("id", "in", partner_ids)]
        else:
            return [("id", "not in", partner_ids)]

    @api.depends_context("company", "date_to")
    def _credit_debit_get(self):
        """Este functia standard la care am adaugat in filtrare si datarea de la date_to"""
        date_to = self.env.context.get("date_to")
        if not date_to:
            return super()._credit_debit_get()

        if not self.ids:
            self.debit = False
            self.credit = False
            return
        query = self.env["account.move.line"]._where_calc(
            [
                ("parent_state", "=", "posted"),
                ("company_id", "child_of", self.env.company.root_id.id),
                ("date", "<=", date_to),
            ]
        )
        self.env["account.move.line"].flush_model(
            ["account_id", "amount_residual", "company_id", "parent_state", "partner_id", "reconciled"]
        )
        self.env["account.account"].flush_model(["account_type"])

        tables, where_clause, where_params = query.get_sql()
        where_params = [tuple(self.ids)] + where_params

        sql = """
            SELECT account_move_line.partner_id, a.account_type, SUM(
                CASE
                    WHEN a.account_type = 'asset_receivable' THEN account_move_line.debit - account_move_line.credit
                    ELSE account_move_line.credit - account_move_line.debit
                END
            )
            FROM {}
            LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
            WHERE a.account_type IN ('asset_receivable','liability_payable')
            AND account_move_line.partner_id IN {}
            AND {}
            GROUP BY account_move_line.partner_id, a.account_type
            """.format(tables, "%s", where_clause or "TRUE")

        self._cr.execute(sql, where_params)
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
