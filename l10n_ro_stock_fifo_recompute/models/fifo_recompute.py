# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict, deque
from datetime import datetime, timedelta

from odoo import Command, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

# Move types whose correction only moves value between stock accounts: they do
# not touch the result, so they stay on the stock accounts in a closed year.
TRANSFER_TYPES = ("internal_transfer", "internal_transit_out", "internal_transit_in")
# Move types dated by the invoice when they are not made on a notice (aviz).
INVOICE_DATED_TYPES = {
    "reception": ("purchase_line_id", "in_invoice"),
    "reception_return": ("purchase_line_id", "in_refund"),
    "delivery": ("sale_line_id", "out_invoice"),
    "delivery_return": ("sale_line_id", "out_refund"),
}
# Stop the fixed point on negative stock settlements after this many passes.
MAX_PASSES = 10


class L10nRoFifoRecompute(models.Model):
    _name = "l10n.ro.fifo.recompute"
    _description = "FIFO Valuation Recompute"
    _order = "id desc"
    _check_company_auto = True

    name = fields.Char(default="/", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("applied", "Applied")],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
    )
    product_ids = fields.Many2many(
        "product.product",
        string="Products",
        check_company=True,
        help="Leave empty, together with the categories, to recompute every FIFO product of the company.",
    )
    categ_ids = fields.Many2many("product.category", string="Product Categories")
    date = fields.Date(
        string="Correction Date",
        required=True,
        default=fields.Date.context_today,
        help="Accounting date of the correction entry, in an open period.",
    )
    closed_year_date = fields.Date(
        string="Last Closed Year End",
        default=lambda self: self._default_closed_year_date(),
        help="Differences on moves dated up to this date belong to a closed "
        "financial year and are posted on the closed years account instead of "
        "the expense account.",
    )
    account_closed_id = fields.Many2one(
        "account.account",
        string="Closed Years Account",
        check_company=True,
        default=lambda self: self._default_account_closed(),
        help="Account for the differences of closed financial years, usually 1174 (OMFP 1802/2014, point 67).",
    )
    line_ids = fields.One2many("l10n.ro.fifo.recompute.line", "recompute_id", string="Differences")
    check_ids = fields.One2many("l10n.ro.fifo.recompute.check", "recompute_id", string="Account Control")
    line_count = fields.Integer(compute="_compute_totals")
    total_delta = fields.Monetary(string="Total Difference", compute="_compute_totals")
    account_move_id = fields.Many2one("account.move", string="Correction Entry", readonly=True, copy=False)

    @api.model
    def _default_closed_year_date(self, company=None):
        """End of the last financial year closed at the lock date of the
        company. A company locking month by month (lock date 31.10) still has
        an open year: only the year ended before it is closed."""
        company = company or self.env.company
        lock_date = company.fiscalyear_lock_date
        if not lock_date:
            return False
        year = company.compute_fiscalyear_dates(lock_date)
        if lock_date >= year["date_to"]:
            return year["date_to"]
        return year["date_from"] - timedelta(days=1)

    @api.model
    def _default_account_closed(self):
        return self.env["account.account"].search(
            [
                ("code", "=like", "1174%"),
                ("company_ids", "in", self.env.company.id),
            ],
            limit=1,
        )

    @api.depends("line_ids.delta")
    def _compute_totals(self):
        for recompute in self:
            recompute.line_count = len(recompute.line_ids)
            recompute.total_delta = sum(recompute.line_ids.mapped("delta"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("l10n.ro.fifo.recompute") or "/"
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_compute(self):
        for recompute in self:
            if recompute.state == "applied":
                raise UserError(self.env._("An applied recompute cannot be computed again."))
            if recompute.closed_year_date and not recompute.account_closed_id:
                raise UserError(
                    self.env._(
                        "Set the closed years account: the differences of a "
                        "closed financial year cannot go to the expense account."
                    )
                )
            recompute.line_ids.unlink()
            recompute.check_ids.unlink()
            recompute.with_company(recompute.company_id)._compute_differences()
            recompute.state = "computed"
        return True

    def action_apply(self):
        for recompute in self:
            if recompute.state != "computed":
                raise UserError(self.env._("Compute the differences first."))
            recompute._check_correction_date()
            recompute.with_company(recompute.company_id)._apply_differences()
            recompute.state = "applied"
        return True

    def _check_correction_date(self):
        """Refuse a correction date in a locked period. Odoo would post the
        entry on the first open date instead, while the values of the moves
        are corrected anyway: the entry and the moves would then disagree on
        the period."""
        self.ensure_one()
        journal = self.company_id.account_stock_journal_id
        if self.company_id._get_violated_lock_dates(self.date, False, journal):
            raise UserError(
                self.env._(
                    "The correction date %(date)s is in a locked period. Choose a date in an open period.",
                    date=self.date,
                )
            )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_applied(self):
        if any(recompute.state == "applied" for recompute in self):
            raise UserError(
                self.env._("An applied recompute cannot be deleted: it is the trace of its correction entry.")
            )

    def action_view_account_move(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": self.account_move_id.id,
            "view_mode": "form",
        }

    # ------------------------------------------------------------------
    # Products and dates
    # ------------------------------------------------------------------
    def _get_products(self):
        """FIFO products of the run, valued like the per-location FIFO engine
        (no lot valuation)."""
        self.ensure_one()
        products = self.product_ids
        if self.categ_ids:
            products |= self.env["product.product"].search([("categ_id", "child_of", self.categ_ids.ids)])
        if not self.product_ids and not self.categ_ids:
            moved = self.env["stock.move"]._read_group(
                [
                    ("company_id", "=", self.company_id.id),
                    ("state", "=", "done"),
                ],
                groupby=["product_id"],
            )
            products = self.env["product.product"].concat(*(p for (p,) in moved))
        return products.with_company(self.company_id).filtered(
            lambda p: p.is_storable and p.cost_method == "fifo" and not p.lot_valuated
        )

    @api.model
    def _get_effective_date(self, move):
        """Date of the move in the FIFO order: a reception or a delivery not
        made on a notice (aviz) is dated by its invoice; any other move keeps
        its own date."""
        line_field, invoice_type = INVOICE_DATED_TYPES.get(move.l10n_ro_move_type, (None, None))
        order_line = line_field and move[line_field]
        if order_line:
            invoice_dates = [
                aml.move_id.invoice_date
                for aml in order_line.invoice_lines
                if aml.parent_state == "posted" and aml.move_id.move_type == invoice_type and aml.move_id.invoice_date
            ]
            if invoice_dates:
                return datetime.combine(min(invoice_dates), move.date.time())
        return move.date

    # ------------------------------------------------------------------
    # FIFO replay
    # ------------------------------------------------------------------
    def _get_product_moves(self, product):
        moves = self.env["stock.move"].search(
            [
                ("product_id", "=", product.id),
                ("company_id", "=", self.company_id.id),
                ("state", "=", "done"),
                "|",
                "|",
                ("is_in", "=", True),
                ("is_out", "=", True),
                # An internal transfer is not always flagged both in and out
                # (out only inside a warehouse, neither when migrated from an
                # older version), yet the goods did move between the locations.
                ("l10n_ro_move_type", "=", "internal_transfer"),
            ]
        )
        dates = {move.id: self._get_effective_date(move) for move in moves}
        return moves.sorted(lambda m: (dates[m.id], m.id)), dates

    def _replay_product(self, product, moves, settled_before):
        """Walk the done moves of ``product`` in chronological order with one
        FIFO queue per location and return the value each move should have.

        ``settled_before`` maps an outgoing move consumed on negative stock to
        the ``(quantity, value)`` of the incoming moves that covered it in the
        previous pass; the replay is repeated until it no longer changes."""
        rounding = product.uom_id.rounding

        def is_zero(quantity):
            return float_is_zero(quantity, precision_rounding=rounding)

        queues = defaultdict(deque)  # location id -> [[quantity, unit value]]
        pending = defaultdict(deque)  # location id -> [[move id, quantity]]
        settled = defaultdict(lambda: [0.0, 0.0])
        settled_used = defaultdict(float)
        values = {}
        valued_qty = {}

        def fallback_unit(move):
            quantity = move._get_valued_qty()
            return move.value / quantity if quantity else product.standard_price

        def negative_value(move, quantity):
            """Value of a quantity taken out of an empty location: at the price
            of the incoming moves that covered it, else as valued today."""
            qty_settled, value_settled = settled_before.get(move.id, (0.0, 0.0))
            available = max(qty_settled - settled_used[move.id], 0.0)
            take = min(available, quantity)
            settled_used[move.id] += take
            value = take * value_settled / qty_settled if qty_settled else 0.0
            return value + (quantity - take) * fallback_unit(move)

        def consume(move, location_id, quantity):
            value = 0.0
            queue = queues[location_id]
            while not is_zero(quantity) and queue:
                layer = queue[0]
                take = min(layer[0], quantity)
                value += take * layer[1]
                layer[0] -= take
                quantity -= take
                if is_zero(layer[0]):
                    queue.popleft()
            if not is_zero(quantity) and quantity > 0:
                pending[location_id].append([move.id, quantity])
                value += negative_value(move, quantity)
            return value

        def receive(location_id, quantity, value):
            unit = value / quantity if quantity else 0.0
            waiting = pending[location_id]
            while not is_zero(quantity) and waiting:
                entry = waiting[0]
                take = min(entry[1], quantity)
                settled[entry[0]][0] += take
                settled[entry[0]][1] += take * unit
                entry[1] -= take
                quantity -= take
                if is_zero(entry[1]):
                    waiting.popleft()
            if not is_zero(quantity) and quantity > 0:
                queues[location_id].append([quantity, unit])

        for move in moves:
            out_value = None
            if self._is_internal_transfer(move):
                # Consume from the source and enter the destination with the
                # value consumed, like the engine does for new transfers.
                out_value = 0.0
                lines = self._get_transfer_lines(move)
                for line in lines:
                    line_qty = line.quantity_product_uom
                    line_value = consume(move, line.location_id.id, line_qty)
                    receive(line.location_dest_id.id, line_qty, line_value)
                    out_value += line_value
                valued_qty[move.id] = sum(lines.mapped("quantity_product_uom"))
                values[move.id] = out_value
                continue
            if move.is_out:
                out_value = 0.0
                lines = move._get_out_move_lines()
                for line in lines:
                    out_value += consume(move, line.location_id.id, line.quantity_product_uom)
                valued_qty[move.id] = sum(lines.mapped("quantity_product_uom"))
            if move.is_in:
                lines = move._get_in_move_lines()
                quantity = sum(lines.mapped("quantity_product_uom"))
                in_value = self._get_in_value(move, out_value, values, valued_qty)
                for line in lines:
                    line_qty = line.quantity_product_uom
                    receive(
                        line.location_dest_id.id,
                        line_qty,
                        in_value * line_qty / quantity if quantity else 0.0,
                    )
                valued_qty.setdefault(move.id, quantity)
                values[move.id] = in_value
            else:
                values[move.id] = out_value
        pending_left = defaultdict(float)
        for waiting in pending.values():
            for move_id, quantity in waiting:
                pending_left[move_id] += quantity
        remaining = defaultdict(float)
        for location_id, queue in queues.items():
            remaining[location_id] += sum(qty * unit for qty, unit in queue)
        moves_by_id = {move.id: move for move in moves}
        for location_id, waiting in pending.items():
            for move_id, quantity in waiting:
                remaining[location_id] -= quantity * fallback_unit(moves_by_id[move_id])
        return {
            "values": values,
            "settled": {k: tuple(v) for k, v in settled.items()},
            "pending": pending_left,
            "remaining": remaining,
        }

    @api.model
    def _is_internal_transfer(self, move):
        """A transfer between two internal locations, whatever its in/out
        flags: inside a warehouse it is flagged out only, and a transfer
        migrated from an older version neither in nor out."""
        return move.l10n_ro_move_type == "internal_transfer"

    def _get_transfer_lines(self, move):
        """Lines of an internal transfer moving owned goods between two valued
        locations."""
        partner = self.company_id.partner_id
        return move.move_line_ids.filtered(
            lambda ml: ml.location_id._should_be_valued()
            and ml.location_dest_id._should_be_valued()
            and (not ml.owner_id or ml.owner_id == partner)
        )

    @api.model
    def _get_in_value(self, move, out_value, values, valued_qty):
        """Value of an incoming move in the replay."""
        # Internal transfer: what left the source enters the destination.
        if out_value is not None:
            return out_value
        # Customer return: the corrected value of the delivery, pro rata.
        origin = move.origin_returned_move_id
        if origin and origin.id in values and valued_qty.get(origin.id):
            return values[origin.id] * move._get_valued_qty() / valued_qty[origin.id]
        # Transit reception: valued from the moves that left for transit.
        origins = move.move_orig_ids
        if origins and not move.purchase_line_id and all(o.id in values for o in origins):
            origin_qty = sum(valued_qty.get(o.id, 0.0) for o in origins)
            if origin_qty:
                origin_value = sum(values[o.id] for o in origins)
                return origin_value * move._get_valued_qty() / origin_qty
        # External reception: its value (bill, order, landed costs) stands.
        return move.value

    def _replay_until_stable(self, product, moves):
        settled = {}
        for _pass in range(MAX_PASSES):
            result = self._replay_product(product, moves, settled)
            if self._same_settlement(settled, result["settled"]):
                break
            settled = result["settled"]
        return result

    def _same_settlement(self, before, after):
        currency = self.company_id.currency_id
        if before.keys() != after.keys():
            return False
        return all(
            currency.is_zero(before[key][1] - after[key][1]) and abs(before[key][0] - after[key][0]) < 1e-6
            for key in after
        )

    # ------------------------------------------------------------------
    # Differences, accounts and control
    # ------------------------------------------------------------------
    def _compute_differences(self):
        self.ensure_one()
        currency = self.company_id.currency_id
        line_vals = []
        remaining_by_account = defaultdict(float)
        products = self._get_products()
        for product in products:
            moves, dates = self._get_product_moves(product)
            if not moves:
                continue
            result = self._replay_until_stable(product, moves)
            for move in moves:
                new_value = currency.round(result["values"].get(move.id, move.value))
                delta = currency.round(new_value - move.value)
                new_pending = result["pending"].get(move.id, 0.0)
                pending_changed = move.is_out and not product.uom_id.is_zero(new_pending - move.fifo_neg_pending_qty)
                if currency.is_zero(delta) and not pending_changed:
                    continue
                line_vals.append(self._prepare_line_vals(move, dates[move.id], new_value, new_pending))
            for location_id, value in result["remaining"].items():
                location = self.env["stock.location"].browse(location_id)
                if not location._should_be_valued():
                    continue
                account = self._get_location_stock_account(product, location)
                remaining_by_account[account] += value
        lines = self.env["l10n.ro.fifo.recompute.line"].create(line_vals)
        self._create_checks(products, remaining_by_account, lines)

    def _prepare_line_vals(self, move, effective_date, new_value, new_pending):
        delta = self.company_id.currency_id.round(new_value - move.value)
        # The year of an error is the year it was booked in (OMFP 1802/2014,
        # point 67): the date of the original stock entry, not the invoice date
        # used for the FIFO order.
        entry_date = self._get_entry_date(move)
        closed = bool(self.closed_year_date and entry_date <= self.closed_year_date)
        debit, credit, note = self._get_line_accounts(move, delta, closed)
        amount = delta
        if closed and delta < 0 and debit and credit:
            # A closed year is not reversed in red (OMFP 1802/2014, point 69
            # is for the current year): a correction in black with the
            # accounts swapped, e.g. Dr 371 / Cr 1174. The line shows the
            # accounts and the amount as they are posted.
            debit, credit, amount = credit, debit, -delta
        if new_pending and not note:
            note = self.env._("Negative stock not covered by a later incoming move")
        return {
            "recompute_id": self.id,
            "move_id": move.id,
            "effective_date": effective_date,
            "entry_date": entry_date,
            "current_value": move.value,
            "new_value": new_value,
            "current_pending_qty": move.fifo_neg_pending_qty,
            "new_pending_qty": new_pending,
            "closed_year": closed,
            "account_debit_id": debit.id,
            "account_credit_id": credit.id,
            "amount": amount,
            "no_entry": bool(not debit and not credit and not note and not self.company_id.currency_id.is_zero(delta)),
            "note": note,
        }

    @api.model
    def _get_entry_date(self, move):
        """Accounting date of the original stock entry of ``move``."""
        if move.account_move_id:
            return move.account_move_id.date
        return fields.Date.to_date(move.date)

    def _get_line_accounts(self, move, delta, closed):
        """Net accounts of the correction of ``move``: the accounts of its own
        stock entry, without the legs that cancel out (482 on an internal
        transfer). In a closed year the expense side goes to the closed years
        account."""
        empty = self.env["account.account"]
        if self.company_id.currency_id.is_zero(delta):
            return empty, empty, False
        account_list = move._get_l10n_ro_move_type_account_list()
        if not account_list:
            return (
                empty,
                empty,
                self.env._("No stock entry for this move type: correct it by hand"),
            )
        vals_list = move._get_l10n_ro_move_line_vals_list(account_list, [], forced_value=delta)
        balance = defaultdict(float)
        for vals in vals_list:
            balance[vals["account_id"]] += vals["debit"] - vals["credit"]
        currency = self.company_id.currency_id
        if move.l10n_ro_move_type in TRANSFER_TYPES and all(currency.is_zero(b) for b in balance.values()):
            # Between two locations on the same stock account: only the value
            # of the move changes, there is nothing to post.
            return empty, empty, False
        debit_ids = [a for a, b in balance.items() if not currency.is_zero(b) and (b > 0) == (delta > 0)]
        credit_ids = [a for a, b in balance.items() if not currency.is_zero(b) and (b > 0) != (delta > 0)]
        if len(debit_ids) != 1 or len(credit_ids) != 1:
            return (
                empty,
                empty,
                self.env._("Accounts not determined: correct it by hand"),
            )
        debit = self.env["account.account"].browse(debit_ids)
        credit = self.env["account.account"].browse(credit_ids)
        # A closed year end always comes with a closed years account: the
        # compute is refused otherwise (``action_compute``).
        if closed and move.l10n_ro_move_type not in TRANSFER_TYPES:
            stock = (
                move.product_id.product_tmpl_id.with_context(l10n_ro_stock_move=move)
                .get_product_accounts()
                .get("stock_valuation")
            )
            if debit != stock:
                debit = self.account_closed_id
            elif credit != stock:
                credit = self.account_closed_id
        return debit, credit, False

    def _get_location_stock_account(self, product, location):
        """Stock account holding ``product`` in ``location``, as the stock
        entries of ``l10n_ro_stock_account`` pick it."""
        account = product.product_tmpl_id.get_product_accounts().get("stock_valuation")
        if product.categ_id.l10n_ro_stock_account_change and location.l10n_ro_property_stock_valuation_account_id:
            account = location.l10n_ro_property_stock_valuation_account_id
        warehouse = location.warehouse_id
        if account and warehouse and warehouse.l10n_ro_fiscal_position_id:
            account = warehouse.l10n_ro_fiscal_position_id.map_account(account)
        return account

    def _create_checks(self, products, remaining_by_account, lines):
        delta_by_account = defaultdict(float)
        for line in lines.filtered(lambda rec: rec.account_debit_id and rec.account_credit_id):
            delta_by_account[line.account_debit_id] += line.amount
            delta_by_account[line.account_credit_id] -= line.amount
        accounts = self.env["account.account"].concat(*(a for a in remaining_by_account if a))
        balances = dict(
            self.env["account.move.line"]._read_group(
                [
                    ("account_id", "in", accounts.ids),
                    ("product_id", "in", products.ids),
                    ("company_id", "=", self.company_id.id),
                    ("parent_state", "=", "posted"),
                ],
                groupby=["account_id"],
                aggregates=["balance:sum"],
            )
        )
        self.env["l10n.ro.fifo.recompute.check"].create(
            [
                {
                    "recompute_id": self.id,
                    "account_id": account.id,
                    "stock_value": remaining_by_account[account],
                    "balance": balances.get(account, 0.0),
                    "correction": delta_by_account.get(account, 0.0),
                }
                for account in accounts
            ]
        )

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------
    def _apply_differences(self):
        self.ensure_one()
        currency = self.company_id.currency_id
        lines = self.line_ids.filtered(
            lambda rec: currency.is_zero(rec.delta) or rec.no_entry or (rec.account_debit_id and rec.account_credit_id)
        )
        aml_vals = defaultdict(float)
        for line in lines:
            if currency.is_zero(line.delta) or line.no_entry:
                continue
            amount = line.amount
            debit, credit = line.account_debit_id, line.account_credit_id
            # Negative only in the current year: reversed in red (storno).
            storno = amount < 0
            product = line.move_id.product_id.id
            aml_vals[(debit.id, product, storno, "debit")] += amount
            aml_vals[(credit.id, product, storno, "credit")] += amount
        # Latest manual value of each move, read in one query.
        latest_manual = {}
        for manual in (
            self.env["product.value"].sudo().search([("move_id", "in", lines.move_id.ids)], order="date desc, id desc")
        ):
            latest_manual.setdefault(manual.move_id.id, manual)
        for line in lines:
            move = line.move_id.sudo()
            vals = {"value": line.new_value}
            if move.is_out:
                # Only settle or reduce the negative quantity on record, never
                # add one: the engine would compensate it on the next incoming
                # move of the location, for a move possibly years old.
                pending = min(line.new_pending_qty, move.fifo_neg_pending_qty)
                quantity = move._get_valued_qty()
                unit = line.new_value / quantity if quantity else 0.0
                vals.update(
                    {
                        "fifo_neg_pending_qty": pending,
                        "fifo_neg_origin_value": pending * unit,
                    }
                )
            move.write(vals)
            # A manual value (set by the FIFO split) has priority when the move
            # is valued again: keep it in line, or a later revaluation of an
            # internal transfer would bring the old value back. Writing it does
            # not revalue the move, only creating one does.
            manual = latest_manual.get(move.id)
            if manual:
                manual.write({"value": line.new_value})
        if not aml_vals:
            return
        journal = self.company_id.account_stock_journal_id
        if not journal:
            raise UserError(self.env._("Set a stock journal on the company before applying."))
        label = self.env._("FIFO valuation correction %s", self.name)
        account_move = (
            self.env["account.move"]
            .sudo()
            .create(
                {
                    "ref": label,
                    "journal_id": journal.id,
                    "date": self.date,
                    "company_id": self.company_id.id,
                    "line_ids": [
                        Command.create(
                            {
                                "account_id": account_id,
                                "product_id": product_id,
                                "name": label,
                                "debit": amount if side == "debit" else 0.0,
                                "credit": amount if side == "credit" else 0.0,
                                "is_storno": storno,
                            }
                        )
                        for (account_id, product_id, storno, side), amount in (aml_vals.items())
                        if not currency.is_zero(amount)
                    ],
                }
            )
        )
        account_move._post()
        self.account_move_id = account_move


class L10nRoFifoRecomputeLine(models.Model):
    _name = "l10n.ro.fifo.recompute.line"
    _description = "FIFO Valuation Recompute Difference"
    _order = "effective_date, id"

    recompute_id = fields.Many2one("l10n.ro.fifo.recompute", required=True, ondelete="cascade", index=True)
    currency_id = fields.Many2one(related="recompute_id.currency_id")
    move_id = fields.Many2one("stock.move", required=True, ondelete="cascade")
    product_id = fields.Many2one(related="move_id.product_id", store=True)
    location_id = fields.Many2one(related="move_id.location_id", string="From")
    location_dest_id = fields.Many2one(related="move_id.location_dest_id", string="To")
    move_type = fields.Selection(related="move_id.l10n_ro_move_type")
    reference = fields.Char(related="move_id.reference")
    entry_date = fields.Date(
        help="Date of the original stock entry of the move: it decides whether "
        "the difference belongs to a closed financial year."
    )
    effective_date = fields.Datetime(
        help="Date of the move in the FIFO order: the invoice date for a reception or a delivery not made on a notice."
    )
    quantity = fields.Float(related="move_id.quantity")
    current_value = fields.Monetary()
    new_value = fields.Monetary(string="Correct Value")
    delta = fields.Monetary(string="Difference", compute="_compute_delta", store=True)
    current_pending_qty = fields.Float(string="Current Negative Qty")
    new_pending_qty = fields.Float(
        string="Correct Negative Qty",
        help="Quantity left on negative stock after the recompute. Applying only "
        "settles or reduces the negative quantity on record, it never adds one.",
    )
    closed_year = fields.Boolean()
    account_debit_id = fields.Many2one("account.account", string="Debit Account")
    account_credit_id = fields.Many2one("account.account", string="Credit Account")
    no_entry = fields.Boolean(
        string="No Entry",
        help="Transfer between two locations on the same stock account: only the "
        "value of the move is corrected, nothing is posted.",
    )
    amount = fields.Monetary(
        string="Posted Amount",
        help="Amount of the correction entry on these accounts: the difference, "
        "negative (in red) when the move was overvalued in the current year. "
        "In a closed year the entry is in black, with the accounts swapped.",
    )
    note = fields.Char()

    @api.depends("current_value", "new_value")
    def _compute_delta(self):
        for line in self:
            line.delta = line.new_value - line.current_value


class L10nRoFifoRecomputeCheck(models.Model):
    _name = "l10n.ro.fifo.recompute.check"
    _description = "FIFO Valuation Recompute Account Control"
    _order = "account_id"

    recompute_id = fields.Many2one("l10n.ro.fifo.recompute", required=True, ondelete="cascade", index=True)
    currency_id = fields.Many2one(related="recompute_id.currency_id")
    account_id = fields.Many2one("account.account", required=True)
    stock_value = fields.Monetary(
        string="Recomputed Stock Value",
        help="Value of the stock left in the locations of this account, after the recompute.",
    )
    balance = fields.Monetary(
        string="Account Balance",
        help="Posted balance of the account for the products of the run.",
    )
    correction = fields.Monetary(help="Effect of the correction entry on the account.")
    balance_after = fields.Monetary(string="Balance After Correction", compute="_compute_difference", store=True)
    difference = fields.Monetary(
        string="Remaining Difference",
        compute="_compute_difference",
        store=True,
        help="Balance after the correction minus the recomputed stock value: what the FIFO recompute does not explain.",
    )

    @api.depends("stock_value", "balance", "correction")
    def _compute_difference(self):
        for check in self:
            check.balance_after = check.balance + check.correction
            check.difference = check.balance_after - check.stock_value
