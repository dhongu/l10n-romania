# ©  2008-now Terrabit <office(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _credit_debit_get(self):
        if not self.env.context.get("date_to"):
            return super(ResPartner, self)._credit_debit_get()
        else:
            tables, where_clause, where_params = self.env['account.move.line'].with_context(state='posted', company_id=self.env.company.id)._query_get()
            where_params = [tuple(self.ids)] + where_params
            if where_clause:
                where_clause = 'AND ' + where_clause
            self._cr.execute("""SELECT account_move_line.partner_id, act.type, SUM(account_move_line.debit - account_move_line.credit)
                          FROM """ + tables + """
                          LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                          LEFT JOIN account_account_type act ON (a.user_type_id=act.id)
                          WHERE act.type IN ('receivable','payable')
                          AND account_move_line.partner_id IN %s
                          """ + where_clause + """
                          GROUP BY account_move_line.partner_id, act.type
                          """, where_params)
            treated = self.browse()
            for pid, type, val in self._cr.fetchall():
                partner = self.browse(pid)
                if type == 'receivable':
                    partner.credit = val
                    if partner not in treated:
                        partner.debit = False
                        treated |= partner
                elif type == 'payable':
                    partner.debit = -val
                    if partner not in treated:
                        partner.credit = False
                        treated |= partner
            remaining = (self - treated)
            remaining.debit = False
            remaining.credit = False
