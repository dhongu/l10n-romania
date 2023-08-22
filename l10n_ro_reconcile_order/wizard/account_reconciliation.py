# See README.rst file on addons root folder for license details


from odoo import api, models


class AccountReconciliation(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _prepare_move_lines(self, move_lines, target_currency=False, target_date=False, recs_count=0):
        move_lines = move_lines.sorted(key=lambda m: m.date_maturity or m.date)
        return super(AccountReconciliation, self)._prepare_move_lines(
            move_lines, target_currency, target_date, recs_count
        )
