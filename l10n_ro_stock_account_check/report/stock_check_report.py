# Copyright (C) 2020 NextERP Romania
# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class StockAccountingCheck(models.TransientModel):
    _name = "stock.accounting.check"
    _description = "StockAccountingCheck"

    # Filters fields, used for data computation

    account_id = fields.Many2one("account.account", required=True)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    date_range_id = fields.Many2one("date.range", string="Date range")
    date_from = fields.Date("Start Date", required=True, default=fields.Date.today)
    date_to = fields.Date("End Date", required=True, default=fields.Date.today)

    line_ids = fields.One2many("stock.accounting.check.line", "report_id")

    @api.model
    def default_get(self, fields_list):
        res = super(StockAccountingCheck, self).default_get(fields_list)

        today = fields.Date.context_today(self)
        today = fields.Date.from_string(today)

        from_date = today + relativedelta(day=1, months=0, days=0)
        to_date = today + relativedelta(day=1, months=1, days=-1)

        res["date_from"] = fields.Date.to_string(from_date)
        res["date_to"] = fields.Date.to_string(to_date)
        return res

    @api.onchange("date_range_id")
    def onchange_date_range_id(self):
        """Handle date range change."""
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    def do_compute_product(self):
        self.line_ids.unlink()

        query = """
        SELECT %(report)s as report_id, product_id, sum(svl_value) as amount_svl , sum(aml_value) as amount_aml,
                jsonb_agg(svl_ids) as svl_ids, jsonb_agg(aml_ids) as aml_ids

            FROM
             (  ( select sm.product_id, sum(svl.value) as svl_value , 0 as aml_value,
                    array_agg(svl.id) as svl_ids,
                    array[]::integer[] as aml_ids
                 from stock_valuation_layer as svl
                      left join stock_move as sm on svl.stock_move_id = sm.id
                  where svl.company_id = %(company)s and
                      date_trunc('day',sm.date) >= %(date_from)s  AND
                      date_trunc('day',sm.date) <= %(date_to)s
                  group by sm.product_id)
            union
            select product_id, 0 as svl_value, sum(aml.balance) as aml_value,
                    array[]::integer[] as svl_ids,
                    array_agg(aml.id) as aml_ids
             from account_move_line as aml
                where
                        account_id = %(account)s and
                        parent_state = 'posted' and company_id = %(company)s and
                        date_trunc('day',aml.date) >= %(date_from)s  AND
                        date_trunc('day',aml.date) <= %(date_to)s
             group by product_id
             ) as subq


             group by product_id
             having abs( sum(svl_value) - sum(aml_value) ) > 1

        """
        params = {
            "report": self.id,
            "company": self.company_id.id,
            "account": self.account_id.id,
            "date_from": fields.Date.to_string(self.date_from),
            "date_to": fields.Date.to_string(self.date_to),
        }
        self.env.cr.execute(query, params=params)
        lines = self.env.cr.dictfetchall()
        for line in lines:
            svl_ids = list(sum(line["svl_ids"], []))
            if svl_ids:
                line["svl_ids"] = [(6, 0, svl_ids)]
            else:
                line["svl_ids"] = False

            aml_ids = list(sum(line["aml_ids"], []))
            if aml_ids:
                line["aml_ids"] = [(6, 0, aml_ids)]
            else:
                line["aml_ids"] = False

        self.line_ids.create(lines)

    def button_show_report(self):
        self.do_compute_product()
        action = self.env.ref(
            "l10n_ro_stock_account_check.action_stock_accounting_check_line"
        ).read()[0]
        return action


class StockAccountingCheckLine(models.TransientModel):
    _name = "stock.accounting.check.line"
    _description = "StockAccountingCheckLine"
    _order = "report_id, product_id"
    _rec_name = "product_id"

    report_id = fields.Many2one("stock.accounting.check")
    product_id = fields.Many2one("product.product", string="Product")

    amount_svl = fields.Monetary(currency_field="currency_id", string="Amount SVL")

    amount_aml = fields.Monetary(currency_field="currency_id", string="Amount AML")

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    svl_ids = fields.Many2many("stock.valuation.layer")
    aml_ids = fields.Many2many("account.move.line")

    def action_slv_details(self):
        self.ensure_one()

        action = {
            "name": _("Valuation"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": self.env.context,
            "res_model": "stock.valuation.layer",
            "domain": [("id", "in", self.svl_ids.ids)],
        }

        return action

    def action_aml_details(self):
        self.ensure_one()

        action = {
            "name": _("Account Move Line"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": self.env.context,
            "res_model": "account.move.line",
            "domain": [("id", "in", self.aml_ids.ids)],
        }

        return action

    def get_general_buttons(self):
        return []
