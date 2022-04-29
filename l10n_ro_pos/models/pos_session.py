# ©  2015-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import float_is_zero


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    bank_journal_id = fields.Many2one("account.journal", domain=[("type", "in", ["bank"])])
    receivable_account_id = fields.Many2one("account.account", domain=[])


class PosSession(models.Model):
    _inherit = "pos.session"

    def _reconcile_account_move_lines(self, data):
        if self.company_id.romanian_accounting:
            data["stock_output_lines"] = {}
        return super(PosSession, self)._reconcile_account_move_lines(data)

    def _accumulate_amounts(self, data):
        def get_amounts():
            res = {"amount": 0.0, "amount_converted": 0.0}
            return res

        data = super(PosSession, self)._accumulate_amounts(data)

        amounts = get_amounts

        if self.company_id.romanian_accounting:
            # nu trebuie generate note contabile  pentru ca acestea sunt generate in miscarea de stoc
            data.update(
                {
                    "stock_expense": defaultdict(amounts),
                    "stock_return": defaultdict(amounts),
                    "stock_output": defaultdict(amounts),
                }
            )

        return data

    def _create_cash_statement_lines_and_cash_move_lines(self, data):

        data = super(PosSession, self)._create_cash_statement_lines_and_cash_move_lines(data)
        # data = self._create_bank_statement_lines_and_bank_move_lines(data)

        return data

    def _create_bank_statement_lines_and_bank_move_lines(self, data):

        # MoveLine = data.get("MoveLine")
        split_receivables_bank = data.get("split_receivables")
        combine_receivables_bank = data.get("combine_receivables")

        statements_by_journal_id = {statement.journal_id.id: statement for statement in self.statement_ids}
        # handle split bank payments
        split_bank_statement_line_vals = defaultdict(list)
        split_bank_receivable_vals = defaultdict(list)
        if split_receivables_bank:
            for payment, amounts in split_receivables_bank.items():
                if not payment.payment_method_id.bank_journal_id:
                    continue
                statement = statements_by_journal_id[payment.payment_method_id.bank_journal_id.id]
                split_bank_statement_line_vals[statement].append(
                    self._get_statement_line_vals(
                        statement,
                        payment.payment_method_id.receivable_account_id,
                        amounts["amount"],
                        date=payment.payment_date,
                        partner=payment.pos_order_id.partner_id,
                    )
                )
                split_bank_receivable_vals[statement].append(
                    self._get_split_receivable_vals(payment, amounts["amount"], amounts["amount_converted"])
                )

        # handle combine bank payments
        combine_bank_statement_line_vals = defaultdict(list)
        combine_bank_receivable_vals = defaultdict(list)
        if combine_receivables_bank:
            for payment_method, amounts in combine_receivables_bank.items():
                if not payment_method.bank_journal_id:
                    continue
                if not float_is_zero(amounts["amount"], precision_rounding=self.currency_id.rounding):
                    statement = statements_by_journal_id[payment_method.bank_journal_id.id]
                    combine_bank_statement_line_vals[statement].append(
                        self._get_statement_line_vals(statement, payment_method.receivable_account_id, amounts["amount"])
                    )
                    combine_bank_receivable_vals[statement].append(
                        self._get_combine_receivable_vals(payment_method, amounts["amount"], amounts["amount_converted"])
                    )

        # create the statement lines and account move lines
        bank_statement_line = self.env["account.bank.statement.line"]
        split_bank_statement_lines = {}
        combine_bank_statement_lines = {}
        split_bank_receivable_lines = {}
        combine_bank_receivable_lines = {}
        for statement in self.statement_ids:
            split_bank_statement_lines[statement] = bank_statement_line.create(
                split_bank_statement_line_vals[statement]
            )
            combine_bank_statement_lines[statement] = bank_statement_line.create(
                combine_bank_statement_line_vals[statement]
            )
            # split_bank_receivable_lines[statement] = MoveLine.create(split_bank_receivable_vals[statement])
            # combine_bank_receivable_lines[statement] = MoveLine.create(combine_bank_receivable_vals[statement])

        for payment in split_receivables_bank:
            if not payment.payment_method_id.bank_journal_id:
                continue
            statement = statements_by_journal_id[payment.payment_method_id.bank_journal_id.id]
            statement.write({"balance_end_real": statement.balance_end})

        for payment_method in combine_receivables_bank:
            if not payment_method.bank_journal_id:
                continue
            statement = statements_by_journal_id[payment_method.bank_journal_id.id]
            statement.write({"balance_end_real": statement.balance_end})

        data["split_cash_statement_lines"].update(split_bank_statement_lines)
        data["combine_cash_statement_lines"].update(combine_bank_statement_lines)
        data["split_cash_receivable_lines"].update(split_bank_receivable_lines)
        data["combine_cash_receivable_lines"].update(combine_bank_receivable_lines)

        return data

    @api.model
    def create(self, values):
        session = super(PosSession, self).create(values)

        pos_config = session.config_id
        ctx = dict(self.env.context, company_id=pos_config.company_id.id)
        bank_payment_methods = pos_config.payment_method_ids.filtered(lambda pm: not pm.is_cash_count)
        statement_ids = self.env["account.bank.statement"]
        if self.user_has_groups("point_of_sale.group_pos_user"):
            statement_ids = statement_ids.sudo()
        for bank_journal in bank_payment_methods.mapped("bank_journal_id"):
            ctx["journal_id"] = bank_journal.id if pos_config.cash_control and bank_journal.type == "bank" else False
            st_values = {
                "journal_id": bank_journal.id,
                "user_id": self.env.user.id,
                "name": session.name,
                "pos_session_id": session.id,
            }
            statement_ids |= statement_ids.with_context(ctx).create(st_values)

        return session
