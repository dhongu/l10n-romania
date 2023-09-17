# See README.rst file on addons root folder for license details


from odoo import api, models
from odoo.tools.misc import format_date, parse_date
from odoo.tools.safe_eval import safe_eval


class AccountReconciliation(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def get_move_lines_for_manual_reconciliation(
        self,
        account_id,
        partner_id=False,
        excluded_ids=None,
        search_str=False,
        offset=0,
        limit=None,
        target_currency_id=False,
    ):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        max_lines = safe_eval(get_param("reconcile.max_lines", "15"))
        lines = super().get_move_lines_for_manual_reconciliation(
            account_id=account_id,
            partner_id=partner_id,
            excluded_ids=excluded_ids,
            search_str=search_str,
            offset=offset,
            limit=max_lines or limit,
            target_currency_id=target_currency_id,
        )
        for line in lines:
            line["date_maturity"] = parse_date(self.env, line["date_maturity"])
            line["date"] = parse_date(self.env, line["date"])
        ordered_lines = sorted(lines, key=lambda d: d["date_maturity"] or d["date"])
        for line in ordered_lines:
            line["date_maturity"] = format_date(self.env, line["date_maturity"])
            line["date"] = format_date(self.env, line["date"])
        return ordered_lines
