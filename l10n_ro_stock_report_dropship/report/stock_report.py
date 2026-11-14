# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import fields, models
from odoo.tools import SQL

# Dropship detection: a move whose picking goes from a supplier (or
# company-less transit) location to a customer (or company-less transit)
# location, or the reverse (dropship return). Kept identical to the 18.0
# logic so no dropship movement is lost compared to the previous version.
DROPSHIP_LOCATION_FILTER = """
    (
      ((sl_src.usage = 'supplier' OR (sl_src.usage = 'transit' AND sl_src.company_id IS NULL)) AND
       (sl_dest.usage = 'customer' OR (sl_dest.usage = 'transit' AND sl_dest.company_id IS NULL)))
      OR
      ((sl_src.usage = 'customer' OR (sl_src.usage = 'transit' AND sl_src.company_id IS NULL)) AND
       (sl_dest.usage = 'supplier' OR (sl_dest.usage = 'transit' AND sl_dest.company_id IS NULL)))
    )
"""


class StorageSheet(models.TransientModel):
    _inherit = "l10n.ro.stock.storage.sheet"

    def get_products_with_move_sql(self, product_list=False):
        # Products moved through the standard internal locations.
        res = super().get_products_with_move_sql(product_list=product_list)

        # Dropship products never touch an internal location, so the parent
        # query misses them. Add products having a dropship (supplier<->customer)
        # move in the period.
        product_filter = SQL("AND sm.product_id IN %s", tuple(product_list)) if product_list else SQL()
        query = SQL(
            """
            SELECT sm.product_id as product_id
            FROM stock_move as sm
            LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
            LEFT JOIN stock_location sl_src ON sp.location_id = sl_src.id
            LEFT JOIN stock_location sl_dest ON sp.location_dest_id = sl_dest.id
            WHERE
                sm.state = 'done' AND
                sm.company_id = %(company)s AND
                %(location_filter)s AND
                date_trunc('day', sm.date) >= %(date_from)s AND
                date_trunc('day', sm.date) <= %(date_to)s
                %(product_filter)s
            GROUP BY sm.product_id
            """,
            company=self.company_id.id,
            location_filter=SQL(DROPSHIP_LOCATION_FILTER),
            date_from=self.date_from,
            date_to=self.date_to,
            product_filter=product_filter,
        )
        self.env.cr.execute(query)
        dropship_product_list = [r["product_id"] for r in self.env.cr.dictfetchall()]
        return list(set(res + dropship_product_list))

    def _get_sql_dropship(self, column):
        """Build a dropship insert for the ``in`` or ``out`` side of the sheet.

        Since 19.0 valuation lives on stock.move (``value``/``quantity``) instead
        of on the removed stock.valuation.layer, and a dropship move is a single
        move (no dual reception/delivery layers). A dropship is a pass-through:
        it is reported both on the input and the output side with the same
        positive magnitude so it nets to zero on the on-hand balance (it is
        intentionally excluded from the initial/final queries, which only look
        at internal locations).

        ``account_id`` must carry ``sm.l10n_ro_account_id``: the storage sheet
        groups its rows by account, so a NULL here files every dropship line
        under a separate "no account" group instead of under the goods account
        (371000) the movement is actually valued on. Up to 18.0 the account came
        from the valuation layer, so dropping it on the 19.0 port silently made
        the dropship rows disappear from the account they belong to.

        The result is a plain string on purpose: ``l10n_ro_stock_report`` concatenates
        ``_get_sql_select_in/out`` and executes them with a ``params`` dict, so this
        fragment must keep the same ``%(name)s`` contract. Only module constants are
        interpolated here (column suffix, location filter, lot fields).
        """
        field, select, join, group = self._get_lot_fields()
        amount = f"amount_{column}"
        quantity = f"quantity_{column}"
        unit_price = f"unit_price_{column}"

        sql = f"""
        ;
        insert into l10n_ro_stock_storage_sheet_line
          (report_id, product_id, {amount}, {quantity}, {unit_price},
           account_id, invoice_id, date_time, date, reference,  location_id,
           partner_id, document, valued_type, categ_id {field})
        select * from(

        SELECT  %(report)s as report_id, sm.product_id as product_id,
            COALESCE(sum(sm.value),0)   as {amount},
            COALESCE(ROUND(sum(sm.quantity), 5), 0)   as {quantity},
            CASE
                WHEN ROUND(COALESCE(sum(sm.quantity), 0), 5) != 0
                    THEN COALESCE(sum(sm.value),0) / NULLIF(sum(sm.quantity), 0)
                ELSE 0
            END as {unit_price},
            sm.l10n_ro_account_id as account_id,
            NULL::int as invoice_id,
            sm.date as date_time,
            date_trunc('day', sm.date at time zone 'utc' at time zone %(tz)s) as date,
            sm.reference as reference,
            %(location)s as location_id,
            sp.partner_id,
            sm.reference as document,
            'dropship' as valued_type,
            pt.categ_id as categ_id
            {select}
            from stock_move as sm
                left join stock_picking as sp on sm.picking_id = sp.id
                left join stock_location sl_src ON sp.location_id = sl_src.id
                left join stock_location sl_dest ON sp.location_dest_id = sl_dest.id
                left join product_product prod on prod.id = sm.product_id
                left join product_template pt on pt.id = prod.product_tmpl_id
                {join}
            where
                sm.state = 'done' AND
                sm.company_id = %(company)s AND
                ( %(all_products)s  or sm.product_id in %(product)s ) AND
                sm.date >= %(datetime_from)s  AND  sm.date <= %(datetime_to)s  AND
                {DROPSHIP_LOCATION_FILTER}
            GROUP BY sm.product_id, sm.date,
                     sm.reference, sp.partner_id,
                     sm.l10n_ro_account_id,
                     pt.categ_id {group})
        a
                """
        return sql

    def _get_sql_select_in(self):
        return super()._get_sql_select_in() + self._get_sql_dropship("in")

    def _get_sql_select_out(self):
        return super()._get_sql_select_out() + self._get_sql_dropship("out")

    def do_compute_product(self):
        # The SQL inserts above value dropship lines from ``sm.value``. The amounts
        # are then rewritten from ``stock.move._get_value()``, the value the stock
        # engine posts on the dropship entry (Dr 607 = Cr 371 at the purchase price),
        # so the sheet matches the journal even when the stored value is missing
        # (moves validated before 20.0) or signed differently (dropship returns).
        res = super().do_compute_product()
        self._l10n_ro_recompute_dropship_amounts()
        return res

    def _l10n_ro_recompute_dropship_amounts(self):
        """Fill the value of ``valued_type == 'dropship'`` lines from the moves.

        Each dropship line is one group of the report SQL, keyed by
        (product_id, sm.date, sm.reference, partner_id). The matching done
        dropship moves are read in a single search, grouped on the same key, and
        their ``_get_value()`` is written on the side (in/out) the line represents.
        """
        lines = self.env["l10n.ro.stock.storage.sheet.line"].search(
            [("report_id", "in", self.ids), ("valued_type", "=", "dropship")]
        )
        if not lines:
            return
        moves = (
            self.env["stock.move"]
            .search(
                [
                    ("state", "=", "done"),
                    ("company_id", "in", lines.report_id.company_id.ids),
                    ("product_id", "in", lines.product_id.ids),
                    ("date", "in", list(set(lines.mapped("date_time")))),
                    ("reference", "in", list(set(lines.mapped("reference")))),
                ]
            )
            .filtered(lambda m: m._is_dropshipped() or m._is_dropshipped_returned())
        )
        values = defaultdict(float)
        for move in moves:
            key = (move.company_id.id, move.product_id.id, move.date, move.reference, move.picking_id.partner_id.id)
            values[key] += move.sudo()._get_value()
        for line in lines:
            key = (
                line.report_id.company_id.id,
                line.product_id.id,
                line.date_time,
                line.reference,
                line.partner_id.id,
            )
            value = values.get(key, 0.0)
            if line.quantity_in:
                line.amount_in = value
                line.unit_price_in = value / line.quantity_in
            if line.quantity_out:
                line.amount_out = value
                line.unit_price_out = value / line.quantity_out


class StorageSheetLine(models.TransientModel):
    _inherit = "l10n.ro.stock.storage.sheet.line"

    valued_type = fields.Selection(
        selection_add=[("dropship", "Dropship")],
        ondelete={"dropship": "cascade"},
    )
