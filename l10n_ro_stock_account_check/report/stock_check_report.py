# Copyright (C) 2021 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_is_zero, float_round
from odoo.tools.misc import format_date

_logger = logging.getLogger(__name__)


class StockAccountingCheck(models.TransientModel):
    _name = "stock.accounting.check"
    _description = "StockAccountingCheck"

    # Filters fields, used for data computation

    account_id = fields.Many2one("account.account")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    product_id = fields.Many2one("product.product")
    interval = fields.Boolean(default=True)
    line_details = fields.Boolean()
    date_from = fields.Date("Start Date", required=True, default=fields.Date.today)
    date_to = fields.Date("End Date", required=True, default=fields.Date.today)

    line_ids = fields.One2many("stock.accounting.check.line", "report_id")

    check_purchase = fields.Boolean()
    check_sale = fields.Boolean()
    check_stock_move = fields.Boolean()

    journal_id = fields.Many2one("account.journal")
    picking_type_id = fields.Many2one("stock.picking.type")
    limit = fields.Integer(default=1000)
    all_products = fields.Boolean()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        domain = [
            ("code", "=", "371000"),
            ("company_id", "=", self.env.company.id),
        ]
        account = self.env["account.account"].search(domain, limit=1)
        if account:
            res["account_id"] = account.id
        today = fields.Date.context_today(self)
        today = fields.Date.from_string(today)

        from_date = today + relativedelta(day=1, months=0, days=0, years=-10)
        to_date = today + relativedelta(day=1, months=1, days=-1)

        res["date_from"] = fields.Date.to_string(from_date)
        res["date_to"] = fields.Date.to_string(to_date)

        stock_picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "internal"),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        categories = self.env["product.category"].search([])
        journals = categories.mapped("property_stock_journal")
        if journals:
            res["journal_id"] = journals[0].id
        res["picking_type_id"] = stock_picking_type.id if stock_picking_type else False
        return res

    def do_compute_product(self):
        self.line_ids.unlink()

        _select = ""
        _select_svl = ""
        _select_aml = ""
        _where_svl = ""
        _where_aml = ""
        if  self.all_products:
            _having = ""
        else:
            _having = """
                   having abs( sum(svl_value) - sum(aml_value) ) > 0.1 or
                   abs( sum(svl_value) - sum(remaining_value) ) > 0.1 or
                   abs( sum(quantity_svl) - sum(remaining_qty) ) > 0.1
                """
            if self.interval:
                _where_svl = "AND date_trunc('day',sm.date) >= %(date_from)s  AND date_trunc('day',sm.date) <= %(date_to)s"
                _where_aml = (
                    "AND date_trunc('day',aml.date) >= %(date_from)s  AND date_trunc('day',aml.date) <= %(date_to)s"
                )


        if self.product_id:
            _where_svl += " AND sm.product_id = %(product)s"
            _where_aml += " AND aml.product_id = %(product)s"
            _having = ""

        accounts = self.env["account.account"].search([("code", "=like", "3%")])
        # accounts |= self.env["account.account"].search([("code", "like", "408%")])

        if self.account_id:
            _where_svl += " AND l10n_ro_account_id = %(account)s"
            _where_aml += " AND account_id = %(account)s "
        else:
            _where_svl += " "
            _where_aml += " AND account_id in %(accounts)s"

        if self.line_details:
            _select = ",jsonb_agg(svl_ids) as svl_ids, jsonb_agg(aml_ids) as aml_ids"
            _select_svl = ",array_agg(svl.id) as svl_ids, array[]::integer[] as aml_ids"
            _select_aml = ",array[]::integer[] as svl_ids, array_agg(aml.id) as aml_ids"

        query = f"""
            SELECT %(report)s as report_id, product_id, account_id,
                    sum(svl_value) as amount_svl ,
                    sum(quantity_svl) as quantity_svl,
                    sum(remaining_qty) as remaining_qty,
                    sum(remaining_value) as remaining_value,
                    sum(aml_value) as amount_aml,
                    sum(quantity_aml) as quantity_aml
                    {_select}

                FROM
                 (  ( select sm.product_id, l10n_ro_account_id as account_id,
                        sum(svl.value) as svl_value ,
                        sum(svl.quantity) as quantity_svl,
                        sum(svl.remaining_qty) as remaining_qty,
                        sum(svl.remaining_value) as remaining_value,
                        0 as aml_value,
                        0 as quantity_aml
                        {_select_svl}
                     from stock_valuation_layer as svl
                          left join stock_move as sm on svl.stock_move_id = sm.id
                      where svl.company_id = %(company)s
                            {_where_svl}
                      group by sm.product_id, l10n_ro_account_id)
                union all
                select product_id, account_id,
                        0 as svl_value,
                        0 as quantity_svl,
                        0 as remaining_qty,
                        0 as remaining_value,
                        sum(aml.balance) as aml_value,
                        sum(aml.quantity) as quantity_aml
                        {_select_aml}
                 from account_move_line as aml
                    where
                            product_id is not null and
                            parent_state = 'posted' and
                            company_id = %(company)s
                            {_where_aml}
                 group by product_id, account_id
                 ) as subq


                 group by product_id, account_id
                 {_having}
                 limit %(limit)s
            """

        params = {
            "report": self.id,
            "company": self.company_id.id,
            "account": self.account_id.id,
            "accounts": tuple(accounts.ids),
            "date_from": fields.Date.to_string(self.date_from),
            "date_to": fields.Date.to_string(self.date_to),
            "product": self.product_id.id,
            "limit": self.limit,
        }
        self.env.cr.execute(query, params=params)  # pylint: disable=E8103
        lines = self.env.cr.dictfetchall()
        for line in lines:
            if self.line_details:
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
        query = """
              WITH last_purchase_price_per_product AS (
                    SELECT DISTINCT ON (aml.product_id)
                           aml.product_id,
                           ROUND(aml.price_unit / COALESCE(cr.rate, 1), 2) AS price_unit_company_currency
                    FROM account_move_line aml
                    JOIN account_move am ON aml.move_id = am.id
                    LEFT JOIN LATERAL (
                        SELECT r.rate
                        FROM res_currency_rate r
                        WHERE r.currency_id = am.currency_id
                          AND r.company_id = am.company_id
                          AND r.name <= am.invoice_date
                        ORDER BY r.name DESC
                        LIMIT 1
                    ) cr ON true
                    WHERE am.move_type = 'in_invoice'
                      AND am.state = 'posted'
                      AND aml.product_id IS NOT NULL
                    ORDER BY aml.product_id, am.invoice_date DESC
            )
            UPDATE stock_accounting_check_line sacl
            SET last_purchase_price = lpp.price_unit_company_currency
            FROM last_purchase_price_per_product lpp
            WHERE sacl.product_id = lpp.product_id;
        """
        self.env.cr.execute(query)


    def do_check_purchases(self):
        products = self.line_ids.mapped("product_id")
        purchase_lines = self.env["purchase.order.line"].search([("product_id", "in", products.ids)])
        purchases = purchase_lines.mapped("order_id")
        ok = True
        for purchase in purchases:
            if purchase.invoice_count == 1:
                invoice_date = purchase.invoice_ids.invoice_date or fields.Date.today()
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
                        picking.move_line_ids.write({"date": new_date})
                        ok = False
            if (
                purchase.invoice_status == "to invoice"
                and len(purchase.picking_ids) > 0
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
        sale_lines = self.env["sale.order.line"].search([("product_id", "in", products.ids)])
        sale_orders = sale_lines.mapped("order_id")
        ok = True
        for sale_order in sale_orders:
            if sale_order.invoice_count == 1:
                invoice_date = sale_order.invoice_ids.invoice_date or fields.Date.today()
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
                        # account_move = picking.mapped('move_line_ids.stock_valuation_layer_ids.account_move_id')
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
        stock_moves = self.env["stock.move"].search([("product_id", "in", products.ids)])
        for stock_move in stock_moves:
            stock_move_date = stock_move.date.date()
            account_moves = stock_move.mapped("stock_valuation_layer_ids.account_move_id")
            for account_move in account_moves:
                if account_move.date != stock_move_date and not account_move.activity_ids:
                    note = _(" Nota contabila cu data diferita fata de data %s din miscarea de stoc") % (
                        stock_move_date
                    )

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
        if self.check_purchase:
            if not self.do_check_purchases():
                self.do_compute_product()
        if self.check_sale:
            if not self.do_check_sale_order():
                self.do_compute_product()
        if self.check_stock_move:
            self.do_check_move()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "l10n_ro_stock_account_check.action_stock_accounting_check_line"
        )
        if self.interval:
            action["display_name"] = "{} ({}-{})".format(
                action["name"],
                format_date(self.env, self.date_from),
                format_date(self.env, self.date_to),
            )
        action["context"] = {"line_details": self.line_details, "report_id": self.id}
        action["domain"] = [("report_id", "=", self.id)]
        return action


class StockAccountingCheckLine(models.TransientModel):
    _name = "stock.accounting.check.line"
    _description = "StockAccountingCheckLine"
    _order = "report_id, product_id"
    _rec_name = "product_id"

    report_id = fields.Many2one("stock.accounting.check")

    product_id = fields.Many2one("product.product")
    account_id = fields.Many2one("account.account")
    standard_price = fields.Monetary(currency_field="currency_id", string="Cost Price", compute="_compute_price")
    last_purchase_price = fields.Monetary(currency_field="currency_id", string="Last Purchase Price")
    purchase_price = fields.Monetary(currency_field="currency_id", compute="_compute_price")

    amount = fields.Monetary(currency_field="currency_id", compute="_compute_price")
    price_svl = fields.Monetary(currency_field="currency_id", string="Price SVL", compute="_compute_price")

    price_svl_deviation = fields.Float(string="Price SVL Deviation", compute="_compute_price")

    price_aml = fields.Monetary(currency_field="currency_id", string="Price AML", compute="_compute_price")
    price_aml_deviation = fields.Float(string="Price AML Deviation", compute="_compute_price")

    quantity = fields.Float(compute="_compute_price",  search='_search_quantity')
    quantity_svl = fields.Float(string="Quantity SVL")
    remaining_qty = fields.Float(string="Remaining Quantity SVL")
    remaining_value = fields.Monetary(currency_field="currency_id", string="Remaining Value SVL")
    quantity_aml = fields.Float(string="Quantity AML")

    amount_svl = fields.Monetary(currency_field="currency_id", string="Amount SVL")
    amount_aml = fields.Monetary(currency_field="currency_id", string="Amount AML")

    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    svl_ids = fields.Many2many("stock.valuation.layer")
    aml_ids = fields.Many2many("account.move.line")

    def refresh(self):
        report_id = self.env.context.get("report_id") or self.env.context.get("active_id")
        if report_id:
            report = self.env["stock.accounting.check"].browse(report_id)
            if report:
                report.do_compute_product()
        return {
            "context": self.env.context,
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def _search_quantity(self, operator, value):
        return [("product_id.qty_available", operator, value)]

    def _compute_price(self):
        for line in self:
            product = line.product_id
            standard_price = product.standard_price
            report = line.report_id
            line.quantity = product.with_context(from_date=report.date_from, to_date=report.date_to).qty_available
            line.amount = line.quantity * standard_price
            if float_is_zero(line.quantity_svl, precision_digits=2):
                line.price_svl = standard_price
            else:
                line.price_svl = float_round(line.amount_svl / line.quantity_svl, 2)

            if float_is_zero(line.quantity_aml, precision_digits=2):
                line.price_aml = standard_price
            else:
                line.price_aml = float_round(line.amount_aml / line.quantity_aml, 2)

            if standard_price:
                line.price_svl_deviation = abs(float_round((line.price_svl - standard_price) / standard_price * 100, 2))
                line.price_aml_deviation = abs(float_round((line.price_aml - standard_price) / standard_price * 100, 2))
            else:
                line.price_svl_deviation = 0
                line.price_aml_deviation = 0
            line.purchase_price = product.last_purchase_price

            line.standard_price = standard_price

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
            "target": "current",
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
            "target": "current",
        }

        return action

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

    def action_line_details(self):
        report_detail = self.report_id.copy(
            {
                "line_details": True,
                "product_id": self.product_id.id,
                "account_id": self.account_id.id,
            }
        )
        action = report_detail.with_context(active_id=report_detail.id).button_show_report()

        action["target"] = "current"
        return action

    def action_fix_aml(self):
        report = self.mapped("report_id")

        account_move_values = {
            "journal_id": report.journal_id.id,
            "date": report.date_to,
            "ref": _("Stock Accounting Adjustment"),
            "line_ids": [],
        }
        aml = account_move_values["line_ids"]
        total = 0
        for line in self:
            account = line.account_id
            diff = line.amount_svl - line.amount_aml
            qty = line.quantity_svl - line.quantity_aml
            if not diff and not qty:
                continue
            total += diff
            aml.append(
                (
                    0,
                    0,
                    {
                        "account_id": account.id,
                        "product_id": line.product_id.id,
                        "name": _("Stock Accounting Adjustment"),
                        "debit": diff,
                        "credit": 0,
                        "quantity": qty,
                    },
                )
            )
        if aml:
            aml.append(
                (
                    0,
                    0,
                    {
                        "account_id": account.id,
                        "name": _("Stock Accounting Adjustment"),
                        "debit": 0,
                        "credit": total,
                    },
                )
            )
            account_move = self.env["account.move"].create(account_move_values)
            account_move.action_post()
        for line in self:
            line.amount_aml = line.amount_svl
            line.quantity_aml = line.quantity_svl

    def action_fix_svl(self):
        picking_vals = {
            "picking_type_id": self.report_id.picking_type_id.id,
            "state": "done",
            "location_id": self.report_id.picking_type_id.default_location_src_id.id,
            "location_dest_id": self.report_id.picking_type_id.default_location_dest_id.id,
            "company_id": self.report_id.company_id.id,
        }
        picking = self.env["stock.picking"].create(picking_vals)
        move_count = 0
        for line in self:
            post_date = line.report_id.date_to - relativedelta(hour=12)
            amount = float_round(line.amount - line.amount_svl, 2)
            qty = float_round(line.quantity - line.quantity_svl, 2)
            remaining_value = float_round(line.amount - line.remaining_value, 2)
            remaining_qty = float_round(line.quantity - line.remaining_qty, 2)

            if line.quantity_svl < line.remaining_qty:
                qty_to_remove = line.remaining_qty - line.quantity_svl
                svls = self.env["stock.valuation.layer"].search(
                    [
                        ("product_id", "=", line.product_id.id),
                        ("l10n_ro_account_id", "=", line.account_id.id),
                        ("remaining_qty", ">", 0),
                    ],
                )
                for svl in svls:
                    if qty_to_remove > svl.remaining_qty:
                        qty_to_remove -= svl.remaining_qty
                        svl.write({"remaining_qty": 0})
                    else:
                        svl.write({"remaining_qty": svl.remaining_qty - qty_to_remove})
                        qty_to_remove = 0
                        break
                remaining_qty = -qty_to_remove

            if line.amount_svl < line.remaining_value:
                amount_to_remove = line.remaining_value - line.amount_svl
                svls = self.env["stock.valuation.layer"].search(
                    [
                        ("product_id", "=", line.product_id.id),
                        ("l10n_ro_account_id", "=", line.account_id.id),
                        ("remaining_value", ">", 0),
                    ],
                )
                for svl in svls:
                    if amount_to_remove > svl.remaining_value:
                        amount_to_remove -= svl.remaining_value
                        svl.write({"remaining_value": 0})
                    else:
                        svl.write({"remaining_value": svl.remaining_value - amount_to_remove})
                        amount_to_remove = 0
                        break
                remaining_value = -amount_to_remove

            line.write(
                {
                    "amount_svl": line.amount,
                    "quantity_svl": line.quantity,
                    "remaining_qty": line.quantity,
                    "remaining_value": line.amount,
                }
            )
            if not amount and not qty and not remaining_qty and not remaining_value:
                continue

            if remaining_qty < 0:
                remaining_qty = 0

            stock_move = self.env["stock.move"].create(
                {
                    "name": line.product_id.name,
                    "date": post_date,
                    "product_id": line.product_id.id,
                    "product_uom_qty": qty,
                    "picking_id": picking.id,
                    "location_id": picking.location_id.id,
                    "location_dest_id": line.product_id.property_stock_inventory.id,
                    "company_id": line.report_id.company_id.id,
                    "state": "done",
                }
            )

            svl_values = {
                "l10n_ro_valued_type": "plus_inventory" if amount > 0 else "minus_inventory",
                "product_id": line.product_id.id,
                "value": amount,
                "quantity": qty,
                "remaining_qty": remaining_qty,
                "remaining_value": remaining_value,
                "stock_move_id": stock_move.id,
                "l10n_ro_account_id": line.account_id.id,
                "company_id": line.report_id.company_id.id,
                "create_date": post_date,
            }
            svl = self.env["stock.valuation.layer"].create(svl_values)
            svl.write({"l10n_ro_account_id": line.account_id.id})

            move_count += 1

        if not move_count:
            picking.unlink()
        else:
            picking.write({"state": "done"})

    def action_move_svl_to_product_account(self):
        picking_vals = {
            "picking_type_id": self.report_id.picking_type_id.id,
            "state": "done",
            "location_id": self.report_id.picking_type_id.default_location_src_id.id,
            "location_dest_id": self.report_id.picking_type_id.default_location_dest_id.id,
            "company_id": self.report_id.company_id.id,
        }
        picking = self.env["stock.picking"].create(picking_vals)
        move_count = 0
        for line in self:
            post_date = line.report_id.date_to - relativedelta(hour=12)
            diff = -line.amount_svl
            qty = -line.quantity_svl

            account = (
                line.product_id.l10n_ro_property_stock_valuation_account_id
                or line.product_id.categ_id.property_stock_valuation_account_id
            )

            if account == line.account_id:
                continue

            stock_move = self.env["stock.move"].create(
                {
                    "name": line.product_id.name,
                    "date": post_date,
                    "product_id": line.product_id.id,
                    "product_uom_qty": qty,
                    "picking_id": picking.id,
                    "location_id": picking.location_id.id,
                    "location_dest_id": line.product_id.property_stock_inventory.id,
                    "company_id": line.report_id.company_id.id,
                    "state": "done",
                }
            )

            svl_values = {
                "l10n_ro_valued_type": "plus_inventory" if diff > 0 else "minus_inventory",
                "product_id": line.product_id.id,
                "value": diff,
                "quantity": qty,
                "stock_move_id": stock_move.id,
                "l10n_ro_account_id": line.account_id.id,
                "company_id": line.report_id.company_id.id,
                "create_date": post_date,
            }
            svl = self.env["stock.valuation.layer"].create(svl_values)
            svl.write({"l10n_ro_account_id": line.account_id.id})

            svl_values = {
                "l10n_ro_valued_type": "plus_inventory" if diff < 0 else "minus_inventory",
                "product_id": line.product_id.id,
                "value": -diff,
                "quantity": -qty,
                "stock_move_id": stock_move.id,
                "l10n_ro_account_id": account.id,
                "company_id": line.report_id.company_id.id,
                "create_date": post_date,
            }

            svl = self.env["stock.valuation.layer"].create(svl_values)
            svl.write({"l10n_ro_account_id": account.id})
            line.write({"amount_svl": 0, "quantity_svl": 0})
            move_count += 1

        if not move_count:
            picking.unlink()
        else:
            picking.write({"state": "done"})

    def action_fix_cost_price(self):
        for line in self:
            purchase_price  = max(line.purchase_price, line.last_purchase_price)
            if not purchase_price:
                continue
            line.product_id.with_context(disable_auto_svl=True).write({"standard_price": purchase_price})
