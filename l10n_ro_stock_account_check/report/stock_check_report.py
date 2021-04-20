# Copyright (C) 2021 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.tools.misc import format_date

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
        domain = [
            ("code", "=", "371000"),
            ("company_id", "=", self.env.company.id),
        ]
        account = self.env["account.account"].search(domain, limit=1)
        if account:
            res["account_id"] = account.id
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
        SELECT %(report)s as report_id, product_id, sum(svl_value) as amount_svl ,
         sum(aml_value) as amount_aml,
                jsonb_agg(svl_ids) as svl_ids, jsonb_agg(aml_ids) as aml_ids

            FROM
             (  ( select sm.product_id, sum(svl.value) as svl_value , 0 as aml_value,
                    array_agg(svl.id) as svl_ids,
                    array[]::integer[] as aml_ids
                 from stock_valuation_layer as svl
                      left join stock_move as sm on svl.stock_move_id = sm.id
                  where
                      account_id = %(account)s and
                      svl.company_id = %(company)s and
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

    def do_check_purchases(self):
        products = self.line_ids.mapped("product_id")
        purchase_lines = self.env["purchase.order.line"].search(
            [("product_id", "in", products.ids)]
        )
        purchases = purchase_lines.mapped("order_id")
        ok = True
        for purchase in purchases:
            if purchase.invoice_count == 1:
                invoice_date = purchase.invoice_ids.invoice_date
                for picking in purchase.picking_ids:
                    if invoice_date != picking.date.date() and not picking.notice:
                        new_date = picking.date.replace(
                            year=invoice_date.year,
                            month=invoice_date.month,
                            day=invoice_date.day,
                        )
                        if new_date.hour < 3:
                            new_date = new_date.replace(hour=12)
                        picking.write({"date": new_date})
                        picking.move_lines.write({"date": new_date})
                        ok = False
            if (
                purchase.invoice_status == "to invoice"
                and purchase.picking_count > 0
                and purchase.state not in ["done", "cancel"]
            ):
                if not purchase.activity_ids:
                    note = _("Receptie fara factura")
                    summary = _("Factura lipsa")
                    purchase.activity_schedule(
                        "mail.mail_activity_data_warning",
                        note=note,
                        summary=summary,
                        user_id=purchase.user_id.id,
                    )
        return ok

    def do_check_sale_order(self):
        products = self.line_ids.mapped("product_id")
        sale_lines = self.env["sale.order.line"].search(
            [("product_id", "in", products.ids)]
        )
        sale_oreders = sale_lines.mapped("order_id")
        sale_oreders |= self.env["sale.order"].search(
            [("invoice_status", "=", "to invoice")]
        )
        ok = True
        for sale_order in sale_oreders:
            if sale_order.invoice_count == 1:
                invoice_date = (
                    sale_order.invoice_ids.invoice_date or fields.Date.today()
                )
                for picking in sale_order.picking_ids:
                    if invoice_date != picking.date.date() and not picking.notice:
                        new_date = picking.date.replace(
                            year=invoice_date.year,
                            month=invoice_date.month,
                            day=invoice_date.day,
                        )
                        if new_date.hour < 3:
                            new_date = new_date.replace(hour=12)
                        picking.write({"date": new_date})
                        # picking.move_lines.write({"date": new_date})
                        # account_move = picking.mapped('move_lines.stock_valuation_layer_ids.account_move_id')
                        # account_move.write({'date': invoice_date})
                        ok = False
            if (
                sale_order.invoice_status == "to invoice"
                and sale_order.delivery_count > 0
                and sale_order.state not in ["done", "cancel"]
            ):
                if not sale_order.activity_ids:
                    note = _("Livrare fara factura")
                    summary = _("Factura lipsa")
                    sale_order.activity_schedule(
                        "mail.mail_activity_data_warning",
                        note=note,
                        summary=summary,
                        user_id=sale_order.user_id.id,
                    )
        return ok

    def do_check_move(self):
        products = self.line_ids.mapped("product_id")
        stock_moves = self.env["stock.move"].search(
            [("product_id", "in", products.ids)]
        )
        for stock_move in stock_moves:
            stock_move_date = stock_move.date.date()
            account_moves = stock_move.mapped(
                "stock_valuation_layer_ids.account_move_id"
            )
            for account_move in account_moves:
                if (
                    account_move.date != stock_move_date
                    and not account_move.activity_ids
                ):
                    note = _(
                        " Nota contabila cu data diferita fata de data %s din miscarea de stoc"
                    ) % (stock_move_date)

                    if not stock_move.picking_id:
                        note += " <a href='#' data-oe-model='{}' data-oe-id='{}'>{}</a>".format(
                            "stock.move",
                            stock_move.id,
                            stock_move.name,
                        )
                    else:
                        note += " <a href='#' data-oe-model='{}' data-oe-id='{}'>{}</a>".format(
                            "stock.picking",
                            stock_move.picking_id.id,
                            stock_move.picking_id.name,
                        )

                    summary = _("Data gresit")
                    account_move.activity_schedule(
                        "mail.mail_activity_data_warning",
                        note=note,
                        summary=summary,
                        user_id=account_move.create_uid.id,
                    )

    def button_show_report(self):
        self.do_compute_product()
        if not self.do_check_purchases():
            self.do_compute_product()
        if not self.do_check_sale_order():
            self.do_compute_product()
        self.do_check_move()

        action = self.env.ref(
            "l10n_ro_stock_account_check.action_stock_accounting_check_line"
        ).read()[0]

        action["display_name"] = "{} ({}-{})".format(
            action["name"],
            format_date(self.env, self.date_from),
            format_date(self.env, self.date_to),
        )
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

    def action_purchase(self):

        stock_moves = self.env["stock.move"]
        purchases = self.env["purchase.order"]
        for svl in self.svl_ids:
            stock_moves |= svl.stock_move_id
            purchases |= svl.stock_move_id.purchase_line_id.order_id

        action = {
            "name": _("Purchase"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": self.env.context,
            "res_model": "purchase.order",
            "domain": [("id", "in", purchases.ids)],
        }
        return action

    def action_sale(self):
        stock_moves = self.env["stock.move"]
        sales = self.env["sale.order"]
        for svl in self.svl_ids:
            stock_moves |= svl.stock_move_id
            sales |= svl.stock_move_id.sale_line_id.order_id

        action = {
            "name": _("Sale"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": self.env.context,
            "res_model": "sale.order",
            "domain": [("id", "in", sales.ids)],
        }
        return action
