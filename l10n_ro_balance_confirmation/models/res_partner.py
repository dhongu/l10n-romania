# ©  2008-now Terrabit <office(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from odoo import api, models
from odoo.tools import SQL, unique

class ResPartner(models.Model):
    _inherit = "res.partner"



    @api.depends_context("company", "date_to")
    def _credit_debit_get(self):
        """ Este functia standard la care am adauga in flitrare si datarea de la date_to"""
        date = self.env.context.get("date_to")
        if not date:
            return super()._credit_debit_get()

        if not self.ids:
            self.debit = False
            self.credit = False
            return
        query = self.env['account.move.line']._where_calc([
            ('parent_state', '=', 'posted'),
            ('company_id', 'child_of', self.env.company.root_id.id),
            ("date", "<=", date),
        ])
        self.env['account.move.line'].flush_model(
            ['account_id', 'amount_residual', 'company_id', 'parent_state', 'partner_id', 'reconciled']
        )
        self.env['account.account'].flush_model(['account_type'])
        sql = SQL("""
            SELECT account_move_line.partner_id, a.account_type, SUM(account_move_line.amount_residual)
            FROM %s
            LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
            WHERE a.account_type IN ('asset_receivable','liability_payable')
            AND account_move_line.partner_id IN %s
            AND account_move_line.reconciled IS NOT TRUE
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
            if account_type == 'asset_receivable':
                partner.credit = val
                if partner not in treated:
                    partner.debit = False
                    treated |= partner
            elif account_type == 'liability_payable':
                partner.debit = -val
                if partner not in treated:
                    partner.credit = False
                    treated |= partner
        remaining = (self - treated)
        remaining.debit = False
        remaining.credit = False
