# Copyright (C) 2018 FOREST AND BIOMASS ROMANIA SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class RomaniaTrialBalanceReport(models.TransientModel):
    """Here, we just define class fields.
    For methods, go more bottom at this file.

    The class hierarchy is :
    * RomaniaTrialBalanceReport
    ** RomaniaTrialBalanceReportAccount
    """

    _name = "l10n_ro_report_trial_balance"
    _description = "Romania Trial Balance"

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()

    only_posted_moves = fields.Boolean()
    hide_account_without_move = fields.Boolean()
    with_special_accounts = fields.Boolean()
    company_id = fields.Many2one("res.company")
    account_ids = fields.Many2many("account.account")

    # Data fields, used to browse report data
    line_account_ids = fields.One2many("l10n_ro_report_trial_balance_account", inverse_name="report_id")

    col_opening_balance = fields.Boolean("Balance Opening Year", default=True)  # solduri initiale an
    col_opening = fields.Boolean("Opening Year", default=False)  # rulaje la inceput de an
    col_initial_balance = fields.Boolean("Balance Initial period", default=False)  # solduri initiale perioada
    col_initial = fields.Boolean("Initial period", default=False)  # sume perecente
    col_period = fields.Boolean("Period", default=True)  # rulaje perioada

    col_cumulative = fields.Boolean("Cumulative", default=True)  # total rulaje (de la inceputul anului)

    col_total = fields.Boolean("Total amount", default=True)  # sume totale
    col_balance = fields.Boolean("Balance", default=True)  # solduri finale

    refresh_report = fields.Boolean("Refresh Report")


class RomaniaTrialBalanceAccountReport(models.TransientModel):
    _name = "l10n_ro_report_trial_balance_account"
    _order = "path, code ASC, name ASC"
    _description = "Romania Trial Balance Report"

    report_id = fields.Many2one("l10n_ro_report_trial_balance", ondelete="cascade", index=True)

    # Data fields, used to keep link with real object
    account_id = fields.Many2one("account.account", index=True, string="Account")

    account_group_id = fields.Many2one("account.group", index=True)

    # Data fields, used for report display
    code = fields.Char()
    name = fields.Char()

    # solduri initiale
    debit_opening_balance = fields.Float(digits=(16, 2))
    credit_opening_balance = fields.Float(digits=(16, 2))

    # rulaje intiale
    debit_opening = fields.Float(digits=(16, 2))
    credit_opening = fields.Float(digits=(16, 2))

    # solduri initiale perioada
    debit_initial_balance = fields.Float(digits=(16, 2))
    credit_initial_balance = fields.Float(digits=(16, 2))

    # sume perecente
    debit_initial = fields.Float(digits=(16, 2))
    credit_initial = fields.Float(digits=(16, 2))

    # rulaje perioada
    debit = fields.Float(digits=(16, 2))
    credit = fields.Float(digits=(16, 2))

    # Rulaje cumulate
    debit_cumulative = fields.Float(digits=(16, 2))
    credit_cumulative = fields.Float(digits=(16, 2))

    # sume totale
    debit_total = fields.Float(digits=(16, 2))
    credit_total = fields.Float(digits=(16, 2))

    # solduri finale
    debit_balance = fields.Float(digits=(16, 2))
    credit_balance = fields.Float(digits=(16, 2))

    # Data fields, used to browse report data
    account_ids = fields.Many2many(comodel_name="account.account", string="Accounts")

    path = fields.Char()

    def compute_path(self):
        for item in self:
            group = item.account_group_id
            item.write({"path": group.parent_path})


class RomaniaTrialBalanceComputeReport(models.TransientModel):
    """Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = "l10n_ro_report_trial_balance"

    def get_reports_buttons(self):
        return [
            {"name": _("Print Preview"), "action": "print_pdf"},
            {"name": _("Export (XLSX)"), "action": "print_xlsx"},
        ]

    def print_pdf(self):
        return self.print_report("qweb-pdf")

    def print_xlsx(self):
        return self.print_report("xlsx")

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        context = dict(self.env.context)
        if report_type == "xlsx":
            report_name = "l10n_ro_report_trial_balance_xlsx"
        else:
            report_name = "l10n_ro_report_trial_balance.l10n_ro_report_trial_balance_qweb"
        action = self.env["ir.actions.report"].search(
            [("report_name", "=", report_name), ("report_type", "=", report_type)],
            limit=1,
        )
        return action.with_context(context).report_action(self)

    def _get_html(self):
        result = {}
        # rcontext = {}
        context = dict(self.env.context)
        report = self.browse(context.get("active_id"))
        if report:
            action = self.env.ref("l10n_ro_report_trial_balance.action_l10n_ro_report_trial_balance_control")
            html = action.render_qweb_html(report.ids)
            result["html"] = html[0]

        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()

    def do_execute(self):
        self.ensure_one()
        domain = [
            ("date_from", "=", self.date_from),
            ("date_to", "=", self.date_to),
            ("id", "!=", self.id),
        ]
        if self.refresh_report:
            report = self.search(domain)
            report.unlink()
            report = False
        else:
            report = self.search(domain, limit=1)
            if report:
                report.write(
                    {
                        "hide_account_without_move": self.hide_account_without_move,
                        "with_special_accounts": self.with_special_accounts,
                        "col_opening_balance": self.col_opening_balance,
                        "col_opening": self.col_opening,
                        "col_initial_balance": self.col_initial_balance,
                        "col_initial": self.col_initial,
                        "col_period": self.col_period,
                        "col_cumulative": self.col_cumulative,
                        "col_total": self.col_total,
                        "col_balance": self.col_balance,
                    }
                )

        if not report:
            self.compute_data_for_report()
            report = self

        return report

    def compute_data_for_report(self):

        self.ensure_one()
        self._inject_account_lines()
        self._compute_path()
        self._compute_account_group_values()
        # Refresh cache because all data are computed with SQL requests
        self.refresh()

    def _compute_path(self):
        self.line_account_ids.compute_path()

    def _inject_account_lines(self):
        """Inject report values for report_trial_balance_account"""
        date_from = fields.Date.from_string(self.date_from)
        fy_start_date = fields.Date.to_string(date_from + relativedelta(day=1, month=1))
        if self.only_posted_moves:
            states = ["posted"]
        else:
            states = ["draft", "posted"]
        if self.account_ids:
            accounts = self.account_ids
        else:
            accounts = self.env["account.account"].search([("company_id", "=", self.company_id.id)])

        if not self.with_special_accounts:
            sp_acc_type = self.env.ref("account.data_account_off_sheet")
            if sp_acc_type:
                accounts = accounts.filtered(lambda a: a.user_type_id.id != sp_acc_type.id)
        query_inject_account = """


    with q1_open as (
            SELECT   account_id,
                                coalesce(sum(open.debit),0) AS debit_opening,
                                coalesce(sum(open.credit),0) AS credit_opening
                FROM  account_move AS move
                    JOIN account_move_line AS open
                        ON open.move_id = move.id AND open.date < %(fy_start_date)s

                WHERE open.account_id in %(accounts)s
                      and move.state in %(states)s
                GROUP BY open.account_id

    ),
     q2_init as (
            SELECT   account_id,
                    coalesce(sum(init.debit),0) AS debit_initial,
                    coalesce(sum(init.credit),0) AS credit_initial
                FROM  account_move AS move
                    JOIN account_move_line AS init
                        ON init.move_id = move.id   AND
                         init.date >= %(fy_start_date)s AND
                         init.date < %(date_from)s

                WHERE init.account_id in %(accounts)s
                and move.state in %(states)s
                GROUP BY init.account_id
    ),

    q3_current as (
            SELECT   account_id,
                    coalesce(sum(current.debit),0) AS debit ,
                    coalesce(sum(current.credit),0) AS credit
                FROM  account_move AS move
                    JOIN account_move_line AS current
                        ON current.move_id = move.id  AND
                        current.date >=%(date_from)s   AND
                         current.date <= %(date_to)s

                WHERE current.account_id in %(accounts)s
                and move.state in %(states)s
                GROUP BY current.account_id
    )



    INSERT INTO
        l10n_ro_report_trial_balance_account
        (
        report_id,  create_uid,  create_date,  account_id,  code, name, account_group_id,

        debit_opening_balance, credit_opening_balance,
        debit_opening, credit_opening,

        debit_initial_balance,  credit_initial_balance,

        debit_initial,  credit_initial,

        debit, credit,

        debit_cumulative,  credit_cumulative,

        debit_total,  credit_total,

        debit_balance,    credit_balance

        )
    SELECT
        %(report_id)s AS report_id,
        %(create_uid)s AS create_uid,
        NOW() AS create_date,
        subselect.id as account_id, subselect.code, subselect.name, subselect.group_id,

        subselect.debit_opening_balance, subselect.credit_opening_balance,

        subselect.debit_opening, subselect.credit_opening,

        subselect.debit_initial_balance, subselect.credit_initial_balance,

        subselect.debit_initial, subselect.credit_initial,

        subselect.debit, subselect.credit,

        debit_initial + debit as debit_cumulative,  credit_initial + credit as credit_cumulative,

        debit_opening_balance + debit_initial + debit as debit_total,
        credit_opening_balance + credit_initial + credit as credit_total,

        subselect.debit_balance,
        subselect.credit_balance


    FROM (
    SELECT

        accounts.*,

        CASE WHEN accounts.debit_opening > accounts.credit_opening
            THEN accounts.debit_opening - accounts.credit_opening
            ELSE 0
        END AS debit_opening_balance,
        CASE WHEN accounts.credit_opening > accounts.debit_opening
            THEN accounts.credit_opening - accounts.debit_opening
            ELSE 0
        END AS credit_opening_balance,

        CASE WHEN accounts.debit_initial > accounts.credit_initial
            THEN accounts.debit_initial - accounts.credit_initial
            ELSE 0
        END AS debit_initial_balance,
        CASE WHEN accounts.credit_initial > accounts.debit_initial
            THEN accounts.credit_initial - accounts.debit_initial
            ELSE 0
        END AS credit_initial_balance,

        CASE WHEN accounts.debit_total > accounts.credit_total
            THEN accounts.debit_total - accounts.credit_total
            ELSE 0
        END AS debit_balance,
        CASE WHEN accounts.credit_total > accounts.debit_total
            THEN accounts.credit_total - accounts.debit_total
            ELSE 0
        END AS credit_balance

    FROM
        (
        SELECT  acc.id, acc.code, acc.name, acc.group_id,
        coalesce(debit_opening,0.0) as debit_opening, coalesce(credit_opening,0.0) as credit_opening,
        coalesce(debit_initial,0.0) as debit_initial, coalesce(credit_initial,0.0) as credit_initial,
        coalesce(debit,0.0) as debit, coalesce(credit,0.0) as credit,

        coalesce(debit_opening,0) + coalesce(debit_initial,0) + coalesce(debit,0)  AS debit_total,
        coalesce(credit_opening,0) + coalesce(credit_initial,0) + coalesce(credit,0) as credit_total

          FROM          account_account acc
          LEFT OUTER JOIN q1_open on q1_open.account_id = acc.id
          LEFT OUTER JOIN q2_init on q2_init.account_id = acc.id
          LEFT OUTER JOIN q3_current on q3_current.account_id = acc.id

          WHERE acc.id in %(accounts)s
          ORDER BY acc.code

         ) as accounts
    ) as subselect

    """

        query_inject_account_params = {
            "report_id": self.id,
            "create_uid": self.env.uid,
            "fy_start_date": str(fy_start_date),
            "date_from": str(self.date_from),
            "date_to": str(self.date_to),
            "states": tuple(states),
            "accounts": accounts._ids,
        }

        # q = query_inject_account % query_inject_account_params

        self.env.cr.execute(query_inject_account, query_inject_account_params)
        # if self.hide_account_without_move:
        #     lines = self.line_account_ids.filtered(lambda a: a.debit_balance == 0 and a.credit_balance == 0)
        #     lines.unlink()

    def _compute_account_group_values(self):
        if not self.account_ids:
            acc_res = self.line_account_ids
            groups = self.env["account.group"].search([])  # ('code_prefix', '!=', False)])

            # if self.account_ids:
            #     all_accounts = self.account_ids
            # else:
            #     all_accounts = self.env['account.account'].search([('company_id', '=', self.company_id.id)])
            #
            #
            # if not self.with_special_accounts:
            #     sp_acc_type = self.env.ref('l10n_ro.data_account_type_not_classified')
            #     if sp_acc_type:
            #         all_accounts = all_accounts.filtered(lambda a: a.user_type_id.id != sp_acc_type.id)

            for group in groups:

                accounts = acc_res.filtered(lambda a: a.account_id.id in group.compute_account_ids.ids)
                # if self.hide_account_without_move:
                #     accounts = accounts.filtered(lambda a: a.debit_balance != 0 or a.credit_balance != 0)
                if accounts:
                    values = {
                        "report_id": self.id,
                        "account_group_id": group.id,
                        "code": group.code_prefix or "",
                        "name": group.name,
                        "path": group.parent_path,
                        "debit_opening_balance": 0.0,
                        "credit_opening_balance": 0.0,
                        "debit_opening": 0.0,
                        "credit_opening": 0.0,
                        "debit_initial_balance": 0.0,
                        "credit_initial_balance": 0.0,
                        "debit_initial": 0.0,
                        "credit_initial": 0.0,
                        "debit": 0.0,
                        "credit": 0.0,
                        "debit_cumulative": 0.0,
                        "credit_cumulative": 0.0,
                        "debit_total": 0.0,
                        "credit_total": 0.0,
                        "debit_balance": 0.0,
                        "credit_balance": 0.0,
                    }
                    for acc in accounts:
                        values["debit_opening_balance"] += acc.debit_opening_balance
                        values["credit_opening_balance"] += acc.credit_opening_balance
                        values["debit_opening"] += acc.debit_opening
                        values["credit_opening"] += acc.credit_opening
                        values["debit_initial_balance"] += acc.debit_initial_balance
                        values["credit_initial_balance"] += acc.credit_initial_balance
                        values["debit_initial"] += acc.debit_initial
                        values["credit_initial"] += acc.credit_initial
                        values["debit"] += acc.debit
                        values["credit"] += acc.credit
                        values["debit_cumulative"] += acc.debit_cumulative
                        values["credit_cumulative"] += acc.credit_cumulative
                        values["debit_total"] += acc.debit_total
                        values["credit_total"] += acc.credit_total
                        values["debit_balance"] += acc.debit_balance
                        values["credit_balance"] += acc.credit_balance
                    self.env["l10n_ro_report_trial_balance_account"].create(values)

                    # newdict = {
                    #     'report_id': self.id,
                    #     'account_group_id': group.id,
                    #     'code': group.code_prefix or '',
                    #     'name': group.name,
                    #
                    #     'debit_opening_balance': sum(acc.debit_opening_balance for acc in accounts),
                    #     'credit_opening_balance': sum(acc.credit_opening_balance for acc in accounts),
                    #
                    #     'debit_opening': sum(acc.debit_opening for acc in accounts),
                    #     'credit_opening': sum(acc.credit_opening for acc in accounts),
                    #
                    #     'debit_initial_balance': sum(acc.debit_initial_balance for acc in accounts),
                    #     'credit_initial_balance': sum(acc.credit_initial_balance for acc in accounts),
                    #
                    #     'debit_initial': sum(acc.debit_initial for acc in accounts),
                    #     'credit_initial': sum(acc.credit_initial for acc in accounts),
                    #     'debit': sum(acc.debit for acc in accounts),
                    #     'credit': sum(acc.credit for acc in accounts),
                    #
                    #     'debit_cumulative': sum(acc.debit_cumulative for acc in accounts),
                    #     'credit_cumulative': sum(acc.credit_cumulative for acc in accounts),
                    #
                    #     'debit_total': sum(acc.debit_total for acc in accounts),
                    #     'credit_total': sum(acc.credit_total for acc in accounts),
                    #     'debit_balance': sum(acc.debit_balance for acc in accounts),
                    #     'credit_balance': sum(acc.credit_balance for acc in accounts),
                    # }
                    # self.env['l10n_ro_report_trial_balance_account'].create(newdict)
