# ©  2008-now Terrabit <office(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from datetime import date

from odoo import api, fields, models
from odoo.tools import SQL


class ResPartner(models.Model):
    _inherit = "res.partner"

    has_debit_credit_at_date = fields.Boolean(
        "Has Debit/Credit at date", compute="_compute_credit_debit_date", search="_search_credit_debit_date"
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

        sql = SQL(
            """
            SELECT account_move_line.partner_id
            FROM %s
            LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
            WHERE a.account_type IN ('asset_receivable','liability_payable')
            AND %s
            GROUP BY account_move_line.partner_id
            HAVING ABS(SUM(
                CASE
                    WHEN a.account_type = 'asset_receivable' THEN account_move_line.debit - account_move_line.credit
                    ELSE account_move_line.credit - account_move_line.debit
                END
            )) > 1
            """,
            query.from_clause,
            query.where_clause or SQL("TRUE"),
        )
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("id", "in", SQL("(%s)", sql))]
        else:
            return [("id", "not in", SQL("(%s)", sql))]

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
        sql = SQL(
            """
            SELECT account_move_line.partner_id, a.account_type, SUM(
                CASE
                    WHEN a.account_type = 'asset_receivable' THEN account_move_line.debit - account_move_line.credit
                    ELSE account_move_line.credit - account_move_line.debit
                END
            )
            FROM %s
            LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
            WHERE a.account_type IN ('asset_receivable','liability_payable')
            AND account_move_line.partner_id IN %s
            AND %s
            GROUP BY account_move_line.partner_id, a.account_type
            """,
            query.from_clause,
            tuple(self.ids),
            query.where_clause or SQL("TRUE"),
        )
        treated = self.browse()
        for pid, account_type, val in self.env.execute_query(sql):
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
