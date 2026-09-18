# Copyright (C) 2021 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from dateutil.relativedelta import relativedelta

from odoo import Command, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import SQL
from odoo.tools.float_utils import float_is_zero, float_round
from odoo.tools.misc import format_date

from ..models.stock_move import INTERNAL_MOVE_TYPES, VALUATION_SIGN

_logger = logging.getLogger(__name__)


def _sign_case(signs, column):
    """Build the CASE expression turning a move type into a signed amount.

    In 18.0 `stock.valuation.layer.value` was already signed; in 19.0
    `stock.move.value` is always positive, so the sign has to come from the
    move type - see VALUATION_SIGN in models/stock_move.py.
    """
    sql = SQL("CASE")
    for move_type, sign in signs.items():
        sql = SQL(
            "%s WHEN %s THEN %s",
            sql,
            SQL("sm.l10n_ro_move_type = %s", move_type),
            SQL("%s * sm.%s", sign, SQL(column)),
        )
    return SQL("%s ELSE 0 END", sql)


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
        # In 19.0 account.account is shared between companies through
        # `company_ids`; `company_id` is no longer a searchable column on it.
        domain = [
            ("code", "=", "371000"),
            ("company_ids", "in", self.env.company.ids),
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
        categories = self.env["product.category"].search([], limit=1000)
        journals = categories.mapped("property_stock_journal")
        if journals:
            res["journal_id"] = journals[0].id
        res["picking_type_id"] = stock_picking_type.id if stock_picking_type else False
        return res

    def _get_valuation_query(self, signs, where):
        """Valuation leg of the check, read from the stock moves."""
        details = SQL(", array[]::integer[] as move_ids, array[]::integer[] as aml_ids")
        if self.line_details:
            details = SQL(", array_agg(sm.id) as move_ids, array[]::integer[] as aml_ids")
        return SQL(
            """
            SELECT sm.product_id,
                   sm.l10n_ro_account_id as account_id,
                   sum(%(value)s) as svl_value,
                   sum(%(quantity)s) as quantity_svl,
                   0 as aml_value,
                   0 as quantity_aml
                   %(details)s
              FROM stock_move as sm
             WHERE sm.state = 'done'
               AND sm.company_id = %(company)s
               AND sm.l10n_ro_move_type IS NOT NULL
               AND sm.l10n_ro_account_id IS NOT NULL
               AND sm.l10n_ro_move_type NOT IN %(internal)s
               %(where)s
             GROUP BY sm.product_id, sm.l10n_ro_account_id
            """,
            value=_sign_case(signs, "value"),
            quantity=_sign_case(signs, "product_qty"),
            details=details,
            company=self.company_id.id,
            internal=INTERNAL_MOVE_TYPES,
            where=where,
        )

    def do_compute_product(self):
        self.line_ids.unlink()

        _where_svl = SQL("")
        _where_aml = SQL("")
        _having = SQL("")
        if not self.all_products:
            _having = SQL(
                """
                having abs( sum(svl_value) - sum(aml_value) ) > 0.1
                """
            )
            if self.interval:
                _where_svl = SQL(
                    """
                    AND date_trunc('day', sm.date) >= %s
                    AND date_trunc('day', sm.date) <= %s
                    """,
                    self.date_from,
                    self.date_to,
                )
                _where_aml = SQL(
                    """
                    AND date_trunc('day', aml.date) >= %s
                    AND date_trunc('day', aml.date) <= %s
                    """,
                    self.date_from,
                    self.date_to,
                )

        if self.product_id:
            _where_svl = SQL("%s AND sm.product_id = %s", _where_svl, self.product_id.id)
            _where_aml = SQL("%s AND aml.product_id = %s", _where_aml, self.product_id.id)
            _having = SQL("")

        if self.account_id:
            _where_valuation = SQL("%s AND sm.l10n_ro_account_id = %s", _where_svl, self.account_id.id)
            _where_aml = SQL("%s AND aml.account_id = %s", _where_aml, self.account_id.id)
        else:
            accounts = self.env["account.account"].search([("code", "=like", "3%")])
            _where_valuation = _where_svl
            _where_aml = SQL("%s AND aml.account_id in %s", _where_aml, tuple(accounts.ids or [0]))

        # Internal moves are left out of both sides - see INTERNAL_MOVE_TYPES in
        # models/stock_move.py.  On the accounting side that means dropping the
        # journal items of the entries those moves generated.
        _where_aml = SQL(
            """%s AND aml.move_id NOT IN (
                   SELECT account_move_id FROM stock_move
                    WHERE account_move_id IS NOT NULL
                      AND l10n_ro_move_type IN %s)""",
            _where_aml,
            INTERNAL_MOVE_TYPES,
        )

        details_select = SQL("")
        details_aml = SQL(", array[]::integer[] as move_ids, array[]::integer[] as aml_ids")
        if self.line_details:
            details_select = SQL(", jsonb_agg(move_ids) as move_ids, jsonb_agg(aml_ids) as aml_ids")
            details_aml = SQL(", array[]::integer[] as move_ids, array_agg(aml.id) as aml_ids")

        query = SQL(
            """
            SELECT %(report)s as report_id, product_id, account_id,
                   sum(svl_value) as amount_svl,
                   sum(quantity_svl) as quantity_svl,
                   sum(aml_value) as amount_aml,
                   sum(quantity_aml) as quantity_aml
                   %(details_select)s
              FROM ( %(valuation)s
                     UNION ALL
                     SELECT aml.product_id, aml.account_id,
                            0 as svl_value,
                            0 as quantity_svl,
                            sum(aml.balance) as aml_value,
                            sum(aml.quantity) as quantity_aml
                            %(details_aml)s
                       FROM account_move_line as aml
                      WHERE aml.product_id is not null
                        AND aml.parent_state = 'posted'
                        AND aml.company_id = %(company)s
                        %(where_aml)s
                      GROUP BY aml.product_id, aml.account_id
                   ) as subq
             GROUP BY product_id, account_id
             %(having)s
             LIMIT %(limit)s
            """,
            report=self.id,
            details_select=details_select,
            valuation=self._get_valuation_query(VALUATION_SIGN, _where_valuation),
            details_aml=details_aml,
            company=self.company_id.id,
            where_aml=_where_aml,
            having=_having,
            limit=self.limit,
        )
        self.env.cr.execute(query)
        lines = self.env.cr.dictfetchall()
        for line in lines:
            if self.line_details:
                move_ids = list(sum(line["move_ids"], []))
                line["move_ids"] = [(6, 0, move_ids)] if move_ids else False

                aml_ids = list(sum(line["aml_ids"], []))
                line["aml_ids"] = [(6, 0, aml_ids)] if aml_ids else False
            else:
                line.pop("move_ids", None)
                line.pop("aml_ids", None)

        self.line_ids.create(lines)

        # Last purchase price, used by the cost price fix.
        self.env.cr.execute(
            SQL(
                """
              WITH last_purchase_price_per_product AS (
                    SELECT DISTINCT ON (aml.product_id)
                           aml.product_id,
                           ROUND(aml.price_unit / COALESCE(cr.rate, 1), 2)
                               AS price_unit_company_currency
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
            WHERE sacl.product_id = lpp.product_id
              AND sacl.report_id = %s;
            """,
                self.id,
            )
        )
        self.line_ids.invalidate_recordset(["last_purchase_price"])

    def do_check_purchases(self):
        products = self.line_ids.mapped("product_id")
        purchase_lines = self.env["purchase.order.line"].search([("product_id", "in", products.ids)])
        purchases = purchase_lines.mapped("order_id")
        ok = True
        for purchase in purchases:
            if purchase.invoice_count == 1:
                invoice_date = purchase.invoice_ids.invoice_date or fields.Date.today()
                for picking in purchase.picking_ids:
                    # `stock.picking.date` was dropped in 19.0; the date the
                    # valuation and the journal entry follow is `date_done`.
                    picking_date = picking.date_done or picking.scheduled_date
                    if not picking_date:
                        continue
                    if invoice_date != picking_date.date() and not picking.l10n_ro_notice:
                        new_date = picking_date.replace(
                            year=invoice_date.year,
                            month=invoice_date.month,
                            day=invoice_date.day,
                        )
                        if new_date.hour < 3:
                            new_date = new_date.replace(hour=12)
                        picking.write({"date_done": new_date})
                        picking.move_ids.write({"date": new_date})
                        picking.move_line_ids.write({"date": new_date})
                        ok = False
            if (
                purchase.invoice_status == "to invoice"
                and len(purchase.picking_ids) > 0
                and purchase.state not in ["done", "cancel"]
            ):
                if not purchase.activity_ids:
                    note = self.env._("Reception without bill")
                    summary = self.env._("Missing bill")
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
                    picking_date = picking.date_done or picking.scheduled_date
                    if not picking_date:
                        continue
                    if invoice_date != picking_date.date() and not picking.l10n_ro_notice:
                        new_date = picking_date.replace(
                            year=invoice_date.year,
                            month=invoice_date.month,
                            day=invoice_date.day,
                        )
                        if new_date.hour < 3:
                            new_date = new_date.replace(hour=12)
                        picking.write({"date_done": new_date})
                        ok = False
            if (
                sale_order.invoice_status == "to invoice"
                and sale_order.delivery_count > 0
                and sale_order.state not in ["done", "cancel"]
            ):
                if not sale_order.activity_ids:
                    note = self.env._("Delivery without invoice")
                    summary = self.env._("Missing invoice")
                    sale_order.activity_schedule(
                        "mail.mail_activity_data_warning",
                        note=note,
                        summary=summary,
                        user_id=sale_order.user_id.id,
                    )
        return ok

    def do_check_move(self):
        products = self.line_ids.mapped("product_id")
        stock_moves = self.env["stock.move"].search([("product_id", "in", products.ids), ("state", "=", "done")])
        for stock_move in stock_moves:
            stock_move_date = stock_move.date.date()
            account_moves = stock_move.account_move_id
            if "l10n_ro_extra_account_move_ids" in stock_move._fields:
                account_moves |= stock_move.l10n_ro_extra_account_move_ids
            for account_move in account_moves:
                if account_move.date != stock_move_date and not account_move.activity_ids:
                    note = self.env._(
                        "Journal entry dated differently from the stock move date %(date)s",
                        date=stock_move_date,
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

                    summary = self.env._("Wrong date")
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
    last_purchase_price = fields.Monetary(currency_field="currency_id")
    purchase_price = fields.Monetary(currency_field="currency_id", compute="_compute_price")

    amount = fields.Monetary(currency_field="currency_id", compute="_compute_price")
    price_svl = fields.Monetary(currency_field="currency_id", string="Valuation Price", compute="_compute_price")

    price_svl_deviation = fields.Float(string="Valuation Price Deviation", compute="_compute_price")

    price_aml = fields.Monetary(currency_field="currency_id", string="Price AML", compute="_compute_price")
    price_aml_deviation = fields.Float(string="Price AML Deviation", compute="_compute_price")

    quantity = fields.Float(compute="_compute_price", search="_search_quantity")
    quantity_svl = fields.Float(string="Valuation Quantity")
    # Up to 18.0 these were stored columns on stock.valuation.layer and came
    # straight out of the report query.  In 19.0 they are unstored computed
    # fields on stock.move, so they are aggregated on demand here - which also
    # keeps the cost out of the way when the columns are not displayed.
    remaining_qty = fields.Float(string="Remaining Quantity", compute="_compute_remaining")
    remaining_value = fields.Monetary(
        currency_field="currency_id",
        string="Remaining Value",
        compute="_compute_remaining",
    )
    quantity_aml = fields.Float(string="Quantity AML")

    amount_svl = fields.Monetary(currency_field="currency_id", string="Valuation Amount")
    amount_aml = fields.Monetary(currency_field="currency_id", string="Amount AML")

    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    move_ids = fields.Many2many("stock.move")
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

    @api.depends("product_id", "account_id")
    def _compute_remaining(self):
        """Aggregate the quantity/value left in the FIFO stack of the product."""
        self.remaining_qty = 0
        self.remaining_value = 0
        lines = self.filtered("product_id")
        if not lines:
            return
        moves = self.env["stock.move"].search(
            [
                ("product_id", "in", lines.product_id.ids),
                ("state", "=", "done"),
                ("is_in", "=", True),
                ("l10n_ro_account_id", "in", lines.account_id.ids),
                ("company_id", "in", lines.report_id.company_id.ids),
            ]
        )
        remaining = {}
        for move in moves:
            key = (move.product_id.id, move.l10n_ro_account_id.id)
            qty, value = remaining.get(key, (0.0, 0.0))
            remaining[key] = (qty + move.remaining_qty, value + move.remaining_value)
        for line in lines:
            qty, value = remaining.get((line.product_id.id, line.account_id.id), (0, 0))
            line.remaining_qty = qty
            line.remaining_value = value

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
            # `last_purchase_price` on the product comes from
            # deltatech_purchase_price, which is not a dependency of this
            # module - it stays optional.
            line.purchase_price = product.last_purchase_price if "last_purchase_price" in product._fields else 0

            line.standard_price = standard_price

    def action_slv_details(self):
        self.ensure_one()

        action = {
            "name": self.env._("Valuation"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "context": self.env.context,
            "res_model": "stock.move",
            "domain": [("id", "in", self.move_ids.ids)],
            "target": "current",
        }

        return action

    def action_aml_details(self):
        self.ensure_one()

        action = {
            "name": self.env._("Account Move Line"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "context": self.env.context,
            "res_model": "account.move.line",
            "domain": [("id", "in", self.aml_ids.ids)],
            "target": "current",
        }

        return action

    def action_purchase(self):
        purchases = self.env["purchase.order"]
        for move in self.move_ids:
            purchases |= move.purchase_line_id.order_id

        action = {
            "name": self.env._("Purchase"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "context": self.env.context,
            "res_model": "purchase.order",
            "domain": [("id", "in", purchases.ids)],
        }
        return action

    def action_sale(self):
        sales = self.env["sale.order"]
        for move in self.move_ids:
            sales |= move.sale_line_id.order_id

        action = {
            "name": self.env._("Sale"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
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
        if len(report) != 1:
            raise UserError(self.env._("Select lines from a single report to adjust them."))

        account_move_values = {
            "journal_id": report.journal_id.id,
            "date": report.date_to,
            "ref": self.env._("Stock Accounting Adjustment"),
            "line_ids": [],
        }
        aml = account_move_values["line_ids"]
        label = self.env._("Stock Accounting Adjustment")
        for line in self:
            diff = line.amount_svl - line.amount_aml
            qty = line.quantity_svl - line.quantity_aml
            if not diff and not qty:
                continue
            # The counterpart has to leave the stock account, otherwise the
            # entry balances 371 against 371 and corrects nothing - which is
            # what this action did up to 18.0.  A stock difference belongs on
            # the expense account of the product, the way an inventory
            # adjustment is booked (OMFP 1802/2014).
            # `_get_product_accounts()` in l10n_ro_stock_account returns the
            # plain product accounts unless a stock move is in the context; the
            # accounts configured per location, and the consumption account
            # substitution, are only applied for a given move.  Take a
            # representative move of the product on this account so the
            # adjustment lands on the same accounts the module uses normally.
            sample_move = self.env["stock.move"].search(
                [
                    ("product_id", "=", line.product_id.id),
                    ("state", "=", "done"),
                    ("l10n_ro_account_id", "=", line.account_id.id),
                    ("company_id", "=", line.report_id.company_id.id),
                ],
                order="date desc",
                limit=1,
            )
            accounts = (
                line.product_id.product_tmpl_id.with_company(line.report_id.company_id)
                .with_context(l10n_ro_stock_move=sample_move or None)
                .get_product_accounts()
            )
            counterpart = accounts.get("expense")
            if not counterpart:
                raise UserError(
                    self.env._(
                        "No expense account found for product %(product)s, the adjustment entry cannot be balanced.",
                        product=line.product_id.display_name,
                    )
                )
            aml.append(
                Command.create(
                    {
                        "account_id": line.account_id.id,
                        "product_id": line.product_id.id,
                        "name": label,
                        "debit": diff if diff > 0 else 0,
                        "credit": -diff if diff < 0 else 0,
                        "quantity": qty,
                    }
                )
            )
            aml.append(
                Command.create(
                    {
                        "account_id": counterpart.id,
                        "product_id": line.product_id.id,
                        "name": label,
                        "debit": -diff if diff < 0 else 0,
                        "credit": diff if diff > 0 else 0,
                    }
                )
            )
        if aml:
            account_move = self.env["account.move"].create(account_move_values)
            account_move.action_post()
        for line in self:
            line.amount_aml = line.amount_svl
            line.quantity_aml = line.quantity_svl

    def action_fix_svl(self):
        """Bring the stock valuation in line with the on-hand quantity and cost.

        Up to 18.0 this wrote stock.valuation.layer rows (and patched their
        `remaining_qty` / `remaining_value`) without touching the accounting.
        In 19.0 the valuation layer is gone: the value lives on the stock move
        and the journal entry is generated from it, so the fix is a real
        inventory adjustment - a move that goes through `_action_done()` so the
        quants move too - carrying the value through `value_manual`, the 19.0
        mechanism for forcing the value of a move.  There is no FIFO remainder
        to patch any more, it is derived from the moves themselves.

        The lines that an inventory adjustment cannot express are refused up
        front rather than booked wrong: a difference in value with no
        difference in quantity is a revaluation of the cost, not a plus or a
        minus of inventory, and a quantity and a value pointing in opposite
        directions would produce an entry with the wrong sign.
        """
        refused = []
        for line in self:
            amount = float_round(line.amount - line.amount_svl, 2)
            qty = float_round(line.quantity - line.quantity_svl, 2)
            if not amount and not qty:
                continue
            if not qty:
                refused.append(
                    self.env._(
                        "%(product)s: the value differs by %(amount)s but the "
                        "quantity matches - use Fix Cost Price instead.",
                        product=line.product_id.display_name,
                        amount=amount,
                    )
                )
            elif amount and (amount > 0) != (qty > 0):
                refused.append(
                    self.env._(
                        "%(product)s: quantity %(qty)s and value %(amount)s go in opposite directions.",
                        product=line.product_id.display_name,
                        qty=qty,
                        amount=amount,
                    )
                )
        if refused:
            raise UserError(
                self.env._(
                    "These lines cannot be corrected by an inventory adjustment:\n%(lines)s",
                    lines="\n".join(refused),
                )
            )

        picking_type = self.report_id.picking_type_id
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "company_id": self.report_id.company_id.id,
            }
        )
        move_count = 0
        for line in self:
            post_date = line.report_id.date_to - relativedelta(hour=12)
            amount = float_round(line.amount - line.amount_svl, 2)
            qty = float_round(line.quantity - line.quantity_svl, 2)
            if not qty:
                continue

            inventory_location = line.product_id.property_stock_inventory
            if qty > 0:
                location_id = inventory_location.id
                location_dest_id = picking.location_dest_id.id
            else:
                # Take the goods out of a location that actually holds them.
                # The default source of the operation type is a configuration
                # choice, not a place where this product necessarily sits, and
                # since 19.0 the adjustment is a real move that has to find the
                # quantity it removes.
                quant = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", line.product_id.id),
                        ("location_id.usage", "=", "internal"),
                        ("company_id", "=", line.report_id.company_id.id),
                        ("quantity", ">", 0),
                    ],
                    order="quantity desc",
                    limit=1,
                )
                location_id = (quant.location_id or picking.location_id).id
                location_dest_id = inventory_location.id

            stock_move = self.env["stock.move"].create(
                {
                    "date": post_date,
                    "product_id": line.product_id.id,
                    "product_uom_qty": abs(qty),
                    "picking_id": picking.id,
                    "location_id": location_id,
                    "location_dest_id": location_dest_id,
                    "company_id": line.report_id.company_id.id,
                }
            )
            stock_move = stock_move.with_context(force_period_date=post_date)
            stock_move._action_confirm()
            stock_move.quantity = abs(qty)
            stock_move.picked = True
            stock_move._action_done()
            stock_move.write({"date": post_date})
            if amount:
                # Forcing the value creates a product.value, which re-runs
                # `_set_value()` on the move; the entry then has to be rebuilt
                # from the new value without recomputing it again.
                stock_move.value_manual = abs(amount)
                stock_move.correction_valuation(recompute_value=False)

            line.write(
                {
                    "amount_svl": line.amount,
                    "quantity_svl": line.quantity,
                }
            )
            move_count += 1

        if not move_count:
            picking.unlink()
        else:
            picking.write({"date_done": fields.Datetime.now()})

    def action_move_svl_to_product_account(self):
        """Re-post the valuation of the product on the account it should use.

        In 18.0 the valuation account was frozen on each stock.valuation.layer,
        so moving it meant writing two compensating layers.  In 19.0
        `stock.move.l10n_ro_account_id` is a stored computed field: recomputing
        it and regenerating the journal entry moves both the valuation and the
        accounting at once.
        """
        for line in self:
            account = (
                line.product_id.l10n_ro_property_stock_valuation_account_id
                or line.product_id.categ_id.property_stock_valuation_account_id
            )
            if not account or account == line.account_id:
                continue
            moves = self.env["stock.move"].search(
                [
                    ("product_id", "=", line.product_id.id),
                    ("state", "=", "done"),
                    ("l10n_ro_account_id", "=", line.account_id.id),
                    ("company_id", "=", line.report_id.company_id.id),
                ]
            )
            if not moves:
                continue
            moves._compute_account()
            moves.flush_recordset(["l10n_ro_account_id", "l10n_ro_transfer_account_id"])
            # Keep the values the moves already carry: the point is to move
            # the accounts, not to reprice history at today's cost.
            moves.correction_valuation(recompute_value=False)
            line.write({"amount_svl": 0, "quantity_svl": 0})

    def action_fix_cost_price(self):
        for line in self:
            purchase_price = max(line.purchase_price, line.last_purchase_price)
            if not purchase_price:
                continue
            product = line.product_id
            if product.cost_method == "fifo":
                # `_change_standard_price` skips FIFO products, so writing the
                # cost here would silently leave the valuation untouched.
                raise UserError(
                    self.env._(
                        "%(product)s is valued in FIFO; its cost comes from the incoming moves and cannot be set here.",
                        product=product.display_name,
                    )
                )
            # `disable_auto_svl`, used up to 18.0, no longer exists; its 19.0
            # counterpart is `disable_auto_revaluation`.  Without it a
            # revaluation entry is booked, and it would be dated today rather
            # than at the end of the reported period.
            product.with_context(
                disable_auto_revaluation=True,
                valuation_date=line.report_id.date_to,
            ).write({"standard_price": purchase_price})
