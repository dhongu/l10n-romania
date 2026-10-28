import calendar
import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, release
from odoo.exceptions import UserError
from odoo.orm.identifiers import NewId
from odoo.tools import SQL, date_utils, format_date
from odoo.tools.misc import formatLang

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
        locked = {"date", "journal_id", "company_id", "name"} & set(vals)
        if locked and self.filtered(lambda r: r.state == "closed"):
            # Mutarea datei sau a casieriei ar muta blocarea fără redeschidere și fără urmă.
            raise UserError(self.env._("A closed cash register cannot be changed; reopen it first."))
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

    # Închiderea zilei (OMFP 2634/2015, Anexa 1 pct. 58 lit. d) și h)): după închidere, contul
    # casei nu mai primește înregistrări datate în ziua închisă sau înaintea ei, până la
    # redeschiderea explicită a registrului.
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")],
        default="open",
        required=True,
        copy=False,
        tracking=True,
    )
    closed_balance = fields.Monetary(
        string="Balance at Closing",
        readonly=True,
        copy=False,
        help="The ending balance frozen when the day was closed.",
    )
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    closed_on = fields.Datetime(readonly=True, copy=False)

    # Monetarul: numărarea fizică a numerarului pe cupiuri, comparată cu soldul scriptic.
    # Se numără în moneda casieriei; la o casierie în valută, soldul scriptic al monetarului este
    # soldul în valută al contului casei, nu cel în lei din `balance_end`.
    count_currency_id = fields.Many2one("res.currency", compute="_compute_count_currency_id")
    count_line_ids = fields.One2many("l10n.ro.cash.register.count.line", "register_id", string="Cash Count", copy=False)
    count_book_balance = fields.Monetary(
        string="Book Balance",
        compute="_compute_counted_amount",
        store=True,
        currency_field="count_currency_id",
        help="Balance of the cash account at the end of the day, in the currency of the cash desk.",
    )
    counted_amount = fields.Monetary(
        string="Counted Cash", compute="_compute_counted_amount", store=True, currency_field="count_currency_id"
    )
    count_difference = fields.Monetary(
        string="Count Difference",
        compute="_compute_counted_amount",
        store=True,
        currency_field="count_currency_id",
        help="Counted cash minus the balance of the cash account: positive is a surplus, negative a shortage.",
    )
    is_counted = fields.Boolean(compute="_compute_counted_amount", store=True)

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

    def _get_sequence_cache(self):
        # Cheia cache-ului din `sequence.mixin` este (format, jurnal), iar registrul și notele
        # jurnalului de casă au același format (CASA/2026/00000): cu cache-ul comun, un registru
        # creat în aceeași tranzacție cu postarea unei note continua contorul notelor.
        # `cr.cache` se golește integral la commit/rollback, deci și cheia proprie.
        return self.env.cr.cache.setdefault("l10n.ro.cash.register.sequence", {})

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

    @api.depends("journal_id.currency_id", "company_id.currency_id")
    def _compute_count_currency_id(self):
        for record in self:
            record.count_currency_id = record.journal_id.currency_id or record.company_id.currency_id

    def _is_foreign_currency_count(self):
        self.ensure_one()
        return self.count_currency_id != self.company_id.currency_id

    @api.depends("count_line_ids.amount", "balance_end", "journal_id.currency_id")
    def _compute_counted_amount(self):
        for record in self:
            record.is_counted = bool(record.count_line_ids)
            record.counted_amount = sum(record.count_line_ids.mapped("amount"))
            record.count_book_balance = record.balance_end
            if record.journal_id and record._is_foreign_currency_count():
                record.count_book_balance = record._get_foreign_currency_balance()
            record.count_difference = record.counted_amount - record.count_book_balance if record.is_counted else 0.0

    def _get_foreign_currency_balance(self):
        """Soldul în valută al contului casei la sfârșitul zilei (5314)."""
        self.ensure_one()
        self.env.cr.execute(
            SQL(
                """
                SELECT SUM(aml.amount_currency)
                  FROM account_move_line aml
                  JOIN account_move am ON aml.move_id = am.id
                 WHERE aml.account_id = %s
                   AND aml.date <= %s
                   AND aml.company_id = %s
                   AND aml.currency_id = %s
                   AND am.state = 'posted'
                """,
                self.journal_id.default_account_id.id,
                self.date,
                self.company_id.id,
                self.count_currency_id.id,
            )
        )
        return self.env.cr.fetchone()[0] or 0.0

    def action_count_cash(self):
        """Adaugă în monetar câte un rând pentru fiecare cupiură activă a monedei casieriei."""
        for register in self:
            if register.state == "closed":
                raise UserError(self.env._("The cash count of a closed day cannot be changed; reopen the day first."))
            denominations = self.env["l10n.ro.cash.denomination"].search(
                [("currency_id", "=", register.count_currency_id.id)]
            )
            if not denominations:
                raise UserError(
                    self.env._(
                        "No denominations are defined for %s. Add them under Accounting > Configuration > "
                        "Cash Denominations.",
                        register.count_currency_id.name,
                    )
                )
            missing = denominations - register.count_line_ids.denomination_id
            self.env["l10n.ro.cash.register.count.line"].create(
                [{"register_id": register.id, "denomination_id": d.id} for d in missing]
            )
        return True

    def _check_cash_count(self):
        """Casieria cu monetar obligatoriu se închide doar numărată și fără diferență nejustificată."""
        for register in self.filtered(lambda r: r.journal_id.l10n_ro_require_cash_count):
            if not register.is_counted:
                raise UserError(
                    self.env._("Count the cash by denomination before closing cash register %s.", register.name)
                )
            if not register.count_currency_id.is_zero(register.count_difference):
                raise UserError(
                    self.env._(
                        "The counted cash of cash register %(register)s differs from the balance of the cash "
                        "account by %(difference)s. Record the difference before closing the day.",
                        register=register.name,
                        difference=formatLang(
                            self.env, register.count_difference, currency_obj=register.count_currency_id
                        ),
                    )
                )

    def _get_count_difference_account(self):
        """Contul implicit al diferenței. Contabilul îl poate schimba (ex. 473 în curs de
        clarificare, 4282 lipsă imputată casierului).

        Ordinea: contul de profit/pierdere al jurnalului de casă; pe planul de conturi RO,
        7588 (plus) și 65882 (lipsă neimputabilă, nedeductibilă); altfel contul de diferențe de
        numerar al companiei. Planul RO nu setează conturile de diferențe ale companiei: Odoo
        creează atunci conturi 999xxx, care nu fac parte din planul de conturi, și le propune și
        pe jurnalele de casă noi. Pe planul RO, un jurnal rămas pe ele contează ca neconfigurat.
        """
        self.ensure_one()
        journal, company = self.journal_id, self.company_id
        surplus = self.count_difference > 0
        account = journal.profit_account_id if surplus else journal.loss_account_id
        company_account = (
            company.default_cash_difference_income_account_id
            if surplus
            else company.default_cash_difference_expense_account_id
        )
        if company.chart_template == "ro" and (not account or account == company_account):
            account = (
                self.env["account.chart.template"]
                .with_company(company)
                .ref("pcg_7588" if surplus else "pcg_65882", raise_if_not_found=False)
            ) or account
        return account or company_account

    def action_record_difference(self):
        self.ensure_one()
        if self.state == "closed":
            raise UserError(self.env._("The day is closed; reopen it before recording the difference."))
        if not self.is_counted or self.count_currency_id.is_zero(self.count_difference):
            raise UserError(self.env._("There is no cash count difference to record."))
        if self._is_foreign_currency_count():
            # Operațiunea de casă înregistrează sume în lei; diferența în valută cere curs și
            # sumă în valută pe nota contabilă.
            raise UserError(
                self.env._(
                    "The difference of a foreign currency cash desk is recorded with a journal entry in %s, "
                    "with the amount in currency.",
                    self.count_currency_id.name,
                )
            )
        action = self.action_operation()
        action["context"].update(
            {
                "default_operation": "in" if self.count_difference > 0 else "out",
                "default_amount": abs(self.count_difference),
                "default_description": self.env._("Cash count difference %s", self.name),
                "default_counterpart_account_id": self._get_count_difference_account().id,
            }
        )
        return action

    def action_print_cash_count(self):
        if self.filtered(lambda r: not r.is_counted):
            raise UserError(self.env._("Count the cash by denomination before printing the cash count."))
        return self.env.ref("l10n_ro_cash_register.action_report_cash_count").report_action(self)

    def action_refresh(self):
        self._compute_balance_start()
        self._compute_balance_end()
        self._compute_move_ids()
        return True

    def action_close(self):
        """Închide ziua: îngheață soldul și blochează înregistrările pe casă în urmă."""
        today = fields.Date.context_today(self)
        for register in self.sorted("date"):
            if register.state == "closed":
                continue
            if register.date > today:
                raise UserError(
                    self.env._("A day in the future cannot be closed (%s).", format_date(self.env, register.date))
                )
            register.action_refresh()
            if register.currency_id.compare_amounts(register.balance_end, 0.0) < 0:
                raise UserError(
                    self.env._(
                        "The balance of cash register %(register)s is negative (%(balance)s): the cash "
                        "desk cannot pay more than it holds. Correct the entries before closing the day.",
                        register=register.name,
                        balance=formatLang(self.env, register.balance_end, currency_obj=register.currency_id),
                    )
                )
            register._check_cash_count()
            register.write(
                {
                    "state": "closed",
                    "closed_balance": register.balance_end,
                    "closed_by_id": self.env.user.id,
                    "closed_on": fields.Datetime.now(),
                }
            )
        return True

    def action_reopen(self):
        """Redeschide ziua și toate zilele închise de după ea, din același jurnal.

        Soldul unei zile se reportează în zilele următoare: o corecție în ziua redeschisă
        schimbă și soldurile lor, deci nu pot rămâne închise.
        """
        for register in self.filtered(lambda r: r.state == "closed").sorted("date"):
            later = self.search(
                [
                    ("journal_id", "=", register.journal_id.id),
                    ("date", ">=", register.date),
                    ("state", "=", "closed"),
                ]
            )
            later.write({"state": "open"})
            for reopened in later:
                reopened.message_post(
                    body=self.env._(
                        "Cash register reopened by %(user)s (closing balance was %(balance)s).",
                        user=self.env.user.name,
                        balance=formatLang(self.env, reopened.closed_balance, currency_obj=reopened.currency_id),
                    )
                )
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_except_closed(self):
        if self.filtered(lambda r: r.state == "closed"):
            raise UserError(self.env._("A closed cash register cannot be deleted; reopen it first."))

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
