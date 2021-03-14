# Copyright (C) 2020 NextERP Romania
# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockAccountingCheck(models.TransientModel):
    _name = "stock.accounting.check"
    _description = "StockAccountingCheck"

    # Filters fields, used for data computation

    account_id = fields.Many2one("account.account")
    line_ids = fields.One2many("stock.accounting.check.line", "report_id")

    def do_compute_product(self):
        self.line_ids.unlink()

        query = """
        SELECT %(report)s as report_id, product_id, sum(svl_value) as amount_svl , sum(aml_value) as amount_aml

            FROM
             (  ( select product_id, sum(svl.value) as svl_value , 0 as aml_value
                 from stock_valuation_layer as svl
                  group by product_id)
            union
            select product_id, 0 as svl_value, sum(aml.balance) as aml_value
             from account_move_line as aml
                where account_id = %(account)s and parent_state = 'posted'
             group by product_id
             ) as subq


             group by product_id
             having abs( sum(svl_value) - sum(aml_value) ) > 1

        """
        params = {"report": self.id, "account": self.account_id.id}
        self.env.cr.execute(query, params=params)
        res = self.env.cr.dictfetchall()
        self.line_ids.create(res)

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
