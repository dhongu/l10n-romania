import calendar
import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, release
from odoo.orm.identifiers import NewId
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class CashRegister(models.Model):
    _name = "l10n.ro.cash.register"
    _description = "Cash Register"
    _inherit = ["mail.thread.main.attachment", "mail.activity.mixin", "sequence.mixin"]
    _order = "date desc"
    _sequence_index = "journal_id"

    def create(self, vals_list):
        records = super().create(vals_list)
        # Ensure numbering is assigned on create if missing
        for rec in records:
            try:
                if (not rec.name or rec.name in ("/", "")) and rec.date and rec.journal_id and isinstance(rec.id, int):
                    rec._set_next_sequence()
            except Exception as e:
                _logger.warning("Error while creating cash register %s: %s", rec, e)
                # In case of concurrent writes, avoid breaking the create
                # The normal compute will still assign a number on next valid change
                pass
        return records

    def write(self, vals):
        res = super().write(vals)
        # If the current write explicitly modifies 'name', respect that change and don't auto-assign now.
        if "name" in vals:
            return res
        # Assign a number on save if it's missing and we have the necessary data
        for rec in self:
            try:
                if (not rec.name or rec.name in ("/", "")) and rec.date and rec.journal_id and isinstance(rec.id, int):
                    rec._set_next_sequence()
            except Exception as e:
                _logger.warning("Error while writing cash register %s: %s", rec, e)
                # Be defensive; don't block writes due to sequencing edge cases
                pass
        return res

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
        default=lambda self: self._get_default_journal_id,
    )
    date = fields.Date(required=True, default=fields.Date.context_today)

    balance_start = fields.Monetary(string="Starting Balance", compute="_compute_balance_start", store=True)

    # Balance end is calculated based on the statement line amounts and real starting balance.
    balance_end = fields.Monetary(
        string="Finished Balance",
        compute="_compute_balance_end",
        store=True,
    )

    move_ids = fields.Many2many("account.move", string="Journal Item", compute="_compute_move_ids")
    move_line_ids = fields.Many2many("account.move.line", string="Journal Item Line", compute="_compute_move_ids")

    _unique_date_journal = models.Constraint(
        "unique(date, journal_id)",
        "Duplicate date",
    )
    # Index unic parțial pe câmpul de secvență, cerut de `sequence.mixin` pentru a evita
    # numerotări duplicate sub încărcare (placeholder-ele '/' și NULL sunt excluse).
    _unique_name = models.UniqueIndex(
        "(name, journal_id) WHERE (name NOT IN ('/', ''))",
        "Another cash register with the same number already exists.",
    )

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
                if not isinstance(item.id, NewId):
                    item._set_next_sequence()

    def _get_last_sequence_domain(self, relaxed=False):
        # pylint: disable=sql-injection
        # EXTENDS account sequence.mixin to mimic account.move behavior
        self.ensure_one()
        if not self.date or not self.journal_id:
            return "WHERE FALSE", {}
        where_string = "WHERE journal_id = %(journal_id)s AND name IS NOT NULL AND name NOT IN ('/', '')"
        param = {"journal_id": self.journal_id.id}

        if not relaxed:
            # Find a reference move name close to our date to deduce the reset rule
            domain = [
                ("journal_id", "=", self.journal_id.id),
                ("id", "!=", self.id or self._origin.id),
                ("name", "not in", ("/", "", False)),
            ]
            reference_name = self.sudo().search(domain + [("date", "<=", self.date)], order="date desc", limit=1).name
            if not reference_name:
                reference_name = self.sudo().search(domain, order="date asc", limit=1).name
            sequence_number_reset = self._deduce_sequence_number_reset(reference_name)
            date_start, date_end, *_ = self._get_sequence_date_range(sequence_number_reset)
            where_string += " AND date BETWEEN %(date_start)s AND %(date_end)s"
            param["date_start"] = date_start
            param["date_end"] = date_end

            # Exclude formats we don't want as in account.move
            if sequence_number_reset in ("year", "year_range"):
                param["anti_regex"] = (
                    self._make_regex_non_capturing(self._sequence_monthly_regex.split("(?P<seq>")[0]) + "$"
                )
            elif sequence_number_reset == "never":
                param["anti_regex"] = (
                    self._make_regex_non_capturing(self._sequence_yearly_regex.split("(?P<seq>")[0]) + "$"
                )
            if param.get("anti_regex"):
                where_string += " AND sequence_prefix !~ %(anti_regex)s "

        return where_string, param

    def _get_starting_sequence(self):
        # Mirror account.move logic: cash journals use yearly numbering
        self.ensure_one()
        move_date = self.date or fields.Date.context_today(self)
        year_part = f"{move_date.year:04d}"
        last_day = int(self.company_id.fiscalyear_last_day)
        last_month = int(self.company_id.fiscalyear_last_month)
        is_staggered_year = last_month != 12 or last_day != 31
        if is_staggered_year:
            max_last_day = calendar.monthrange(move_date.year, last_month)[1]
            last_day = min(last_day, max_last_day)
            if move_date > date(move_date.year, last_month, last_day):
                year_part = "{}-{}".format(
                    move_date.strftime("%y"), (move_date + relativedelta(years=1)).strftime("%y")
                )
            else:
                year_part = "{}-{}".format(
                    (move_date + relativedelta(years=-1)).strftime("%y"), move_date.strftime("%y")
                )
        # For cash register we use yearly pattern like journals of type cash
        # Use 5 digits except when staggered fiscal year where we reduce to 4
        seq_part = "0000" if is_staggered_year else "00000"
        starting_sequence = f"{self.journal_id.code}/{year_part}/{seq_part}"
        return starting_sequence

    def _get_sequence_date_range(self, reset):
        # Support fiscal year ranges like account.move when staggered FY
        if reset not in ("year_range", "year_range_month"):
            return super()._get_sequence_date_range(reset)
        fiscalyear_last_day = self.company_id.fiscalyear_last_day
        fiscalyear_last_month = int(self.company_id.fiscalyear_last_month)
        date_start, date_end = date_utils.get_fiscal_year(
            self.date, day=fiscalyear_last_day, month=fiscalyear_last_month
        )
        if reset == "year_range":
            return (date_start, date_end) + (None, None)
        forced_year_range = (date_start.year, date_end.year)
        month_range = date_utils.get_month(self.date)
        fiscalyear_last_month_max_day = calendar.monthrange(self.date.year, fiscalyear_last_month)[1]
        if fiscalyear_last_day < fiscalyear_last_month_max_day and fiscalyear_last_month == self.date.month:
            if self.date.day <= fiscalyear_last_day:
                return (month_range[0], month_range[1].replace(day=fiscalyear_last_day)) + forced_year_range
            else:
                return (month_range[0].replace(day=fiscalyear_last_day + 1), month_range[1]) + forced_year_range
        else:
            return month_range + forced_year_range

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
                    ("company_id", "=", record.company_id.id),
                    ("move_id.state", "=", "posted"),
                ],
                # Registrul de casă listează operațiunile în ordinea în care s-au petrecut;
                # ordinea implicită a liniilor contabile este descrescătoare și ar produce
                # solduri intermediare care nu au existat niciodată.
                order="date, id",
            )
            record.move_line_ids = move_lines
            record.move_ids = move_lines.mapped("move_id")

    @api.depends("date", "journal_id", "move_ids")
    def _compute_balance_start(self):
        for record in self:
            record.balance_start = 0
            if not record.journal_id:
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

    def action_print(self):
        return self.env.ref("l10n_ro_cash_register.action_report_cash_register").report_action(self)

    def _l10n_ro_software_signature(self):
        """Programul informatic și versiunea, obligatorii pe orice listare.

        OMFP 2634/2015, Anexa 1 pct. 58 lit. k).
        """
        self.ensure_one()
        module = self.env["ir.module.module"].sudo().search([("name", "=", "l10n_ro_cash_register")], limit=1)
        return f"Odoo {release.version} / l10n_ro_cash_register {module.latest_version or ''}".strip()

    def action_receipt(self):
        action = self.journal_id.open_payments_action("inbound", "form")
        action["context"].update(
            {"default_journal_id": self.journal_id.id, "default_date": self.date, "keep_journal": True}
        )
        # action["target"] = "new"
        return action

    def action_payment(self):
        action = self.journal_id.open_payments_action("outbound", "form")
        action["context"].update(
            {"default_journal_id": self.journal_id.id, "default_date": self.date, "keep_journal": True}
        )
        # action["target"] = "new"
        return action

    def action_operation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("l10n_ro_cash_register.action_cash_register_operation")
        action["context"] = {
            "default_journal_id": self.journal_id.id,
            "default_date": self.date,
            "keep_journal": True,
        }
        action["target"] = "new"
        return action
