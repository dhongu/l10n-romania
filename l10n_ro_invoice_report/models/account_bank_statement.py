# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    state = fields.Selection(string='Status', required=True, readonly=True, copy=False, tracking=True, selection=[
            ('open', 'New'),
            ('posted', 'Processing'),
            ('confirm', 'Validated'),
        ], default='open',
        help="The current state of your bank statement:"
             "- New: Fully editable with draft Journal Entries."
             "- Processing: No longer editable with posted Journal entries, ready for the reconciliation."
             "- Validated: All lines are reconciled. There is nothing left to process.")

    line_ids = fields.One2many(default=lambda self: self._default_line_ids(), copy=True)


    def _compute_date_index(self):
        for stmt in self:
            for line in stmt.line_ids:
                if not line.internal_index:
                    line.internal_index = line.sequence


        return super()._compute_date_index()

    @api.depends('line_ids.journal_id')
    def _compute_journal_id(self):
        for statement in self:
            statement.journal_id = statement.line_ids.journal_id

    def _default_line_ids(self):
        journal = self.journal_id
        if not journal:
            if self.env.context.get('default_journal_id'):
                journal = self.env['account.journal'].browse(self.env.context['default_journal_id'])
        return [(0, 0, {
            'statement_id': self.id,
            'journal_id': journal.id,
        })]

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def button_print(self):
        res = self.env.ref(
            "l10n_ro_invoice_report.action_report_statement_line"
        ).report_action(self)
        return res

