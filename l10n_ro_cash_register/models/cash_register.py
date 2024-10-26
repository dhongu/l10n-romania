from odoo import api, fields, models


class CashRegister(models.Model):
    _name = "l10n.ro.cash.register"
    _description = "Cash Register"
    _inherit = ["mail.thread.main.attachment", "mail.activity.mixin", "sequence.mixin"]
    _order = "date desc"

    def _get_default_journal_id(self):
        return self.env["account.journal"].search([("type", "=", "cash")], limit=1)

    name = fields.Char(
        string="Number",
        compute="_compute_name",
        readonly=False,
        store=True,
        copy=False,
        tracking=True,
        index="trigram",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        domain=[("type", "=", "cash")],
        default=_get_default_journal_id,
    )
    date = fields.Date(required=True, default=fields.Date.context_today)

    balance_start = fields.Monetary(string="Starting Balance", compute="_compute_balance_start", store=True)

    # Balance end is calculated based on the statement line amounts and real starting balance.
    balance_end = fields.Monetary(
        string="Computed Balance",
        compute="_compute_balance_end",
        store=True,
    )

    move_ids = fields.Many2many("account.move", string="Journal Items", compute="_compute_move_ids")
    move_line_ids = fields.Many2many("account.move.line", string="Journal Items", compute="_compute_move_ids")

    _sql_constraints = [("unique_date_journal", "unique(date, journal_id)", "Duplicate date")]

    @api.depends("journal_id", "date")
    def _compute_name(self):
        for item in self.sorted(lambda m: m.date):
            move_has_name = item.name and item.name != "/"
            if move_has_name:
                if not item._sequence_matches_date():
                    if item._get_last_sequence():
                        # The name does not match the date and the move is not the first in the period:
                        # Reset to draft
                        item.name = False
                        continue
                else:
                    if move_has_name or not move_has_name and item._get_last_sequence():
                        # The move either
                        # - has a name and was posted before, or
                        # - doesn't have a name, but is not the first in the period
                        # so we don't recompute the name
                        continue
            if item.date and (not move_has_name or not item._sequence_matches_date()):
                item._set_next_sequence()

    def _get_last_sequence_domain(self, relaxed=False):
        # pylint: disable=sql-injection
        # EXTENDS account sequence.mixin
        self.ensure_one()
        if not self.date or not self.journal_id:
            return "WHERE FALSE", {}
        where_string = "WHERE journal_id = %(journal_id)s AND name != '/'"
        param = {"journal_id": self.journal_id.id}
        return where_string, param

    @api.onchange("journal_id")
    def _onchange_journal_id(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.env.company.currency_id

    @api.depends("date", "journal_id")
    def _compute_move_ids(self):
        for record in self:
            move_lines = self.env["account.move.line"].search(
                [
                    ("date", "=", record.date),
                    ("account_id", "=", record.journal_id.default_account_id.id),
                    ("move_id.state", "=", "posted"),
                ]
            )
            record.move_line_ids = move_lines
            record.move_ids = move_lines.mapped("move_id")

    @api.depends("date", "journal_id", "move_ids")
    def _compute_balance_start(self):
        for record in self:
            param = {
                "account_id": record.journal_id.default_account_id.id,
                "date": record.date,
                "company_id": record.company_id.id,
            }
            sql = """
                SELECT SUM(debit-credit) as amount
                FROM account_move_line join account_move on account_move_line.move_id = account_move.id
                WHERE account_id = %(account_id)s
                    AND account_move_line.date < %(date)s
                    AND account_move_line.company_id = %(company_id)s
                    AND account_move.state = 'posted'
            """
            self.env.cr.execute(sql, param)
            row = self.env.cr.dictfetchone()
            record.balance_start = row["amount"] or 0.0

    @api.depends("date", "journal_id", "move_ids")
    def _compute_balance_end(self):
        for record in self:
            if not record.journal_id:
                record.balance_end = 0.0
                continue
            param = {
                "account_id": record.journal_id.default_account_id.id,
                "date": record.date,
                "company_id": record.company_id.id,
            }
            sql = """
                SELECT SUM(debit-credit) as amount
                 FROM account_move_line join account_move on account_move_line.move_id = account_move.id
                WHERE account_id = %(account_id)s
                    AND account_move_line.date <= %(date)s
                    AND account_move_line.company_id = %(company_id)s
                    AND account_move.state = 'posted'
            """
            self.env.cr.execute(sql, param)
            row = self.env.cr.dictfetchone()
            record.balance_end = row["amount"] or 0.0

    def action_refresh(self):
        self._compute_balance_start()
        self._compute_balance_end()
        self._compute_move_ids()
        return True

    def action_receipt(self):
        action = self.journal_id.open_payments_action("inbound", "form")
        action["context"].update({"default_journal_id": self.journal_id.id})
        action["target"] = "new"
        return action

    def action_payment(self):
        action = self.journal_id.open_payments_action("outbound", "form")
        action["context"].update({"default_journal_id": self.journal_id.id})
        action["target"] = "new"
        return action
