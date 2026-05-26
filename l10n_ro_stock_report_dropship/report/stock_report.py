# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StorageSheet(models.TransientModel):
    _inherit = "l10n.ro.stock.storage.sheet"

    def get_products_with_move_sql(self, product_list=False):
        res = super().get_products_with_move_sql(product_list=product_list)
        locations = self.location_ids

        query = """
            SELECT product_id
            FROM stock_move as sm
            LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
            LEFT JOIN stock_location sl_src ON sp.location_id = sl_src.id
            LEFT JOIN stock_location sl_dest ON sp.location_dest_id = sl_dest.id
            WHERE
                    sm.state = 'done' AND
                    sm.company_id = %(company)s AND
                    ((sl_src.usage = 'supplier' OR (sl_src.usage = 'transit' AND sl_src.company_id IS NULL)) AND
                     (sl_dest.usage = 'customer' OR (sl_dest.usage = 'transit' AND sl_dest.company_id IS NULL))) AND
                    date_trunc('day',sm.date) >= %(date_from)s  AND
                    date_trunc('day',sm.date) <= %(date_to)s
            """
        if product_list:
            query += " AND sm.product_id in %(product_list)s"

        query += " GROUP BY product_id"

        params = {
            "date_from": self.date_from,
            "date_to": self.date_to,
            "locations": tuple(locations.ids),
            "product_list": tuple(product_list or []),
            "company": self.company_id.id,
        }
        self.env.cr.execute(query, params=params)
        dropship_product_list = [r[0] for r in self.env.cr.fetchall()]
        return list(set(res + dropship_product_list))

    def _get_sql_select_in(self):
        sql = super()._get_sql_select_in()
        # We need to inject the dropship logic into the SQL.
        # Since it's a large string, we'll use string replacement if possible,
        # but it's risky. A better way is to override the method entirely.
        # Given the complexity of the original SQL, I'll rewrite it with the extension.

        field, select, join, group = self._get_lot_fields()

        sql = f"""
        insert into l10n_ro_stock_storage_sheet_line
          (report_id, product_id, amount_in, quantity_in, unit_price_in,
           account_id, invoice_id, date_time, date, reference,  location_id,
           partner_id, document, valued_type, categ_id {field} )
        select * from(


        SELECT  %(report)s as report_id, sm.product_id as product_id,
            COALESCE(sum(svl_in.value),0)   as amount_in,
            COALESCE(ROUND(sum(svl_in.quantity), 5), 0)   as quantity_in,
            CASE
                WHEN ROUND(COALESCE(sum(svl_in.quantity), 0), 5) != 0
                    THEN COALESCE(sum(svl_in.value),0) / sum(svl_in.quantity)
                ELSE 0
            END as unit_price_in,
             svl_in.l10n_ro_account_id as account_id,
             svl_in.l10n_ro_invoice_id as invoice_id,
            sm.date as date_time,
            date_trunc('day', sm.date at time zone 'utc' at time zone %(tz)s) as date,
            sm.reference as reference,
            %(location)s as location_id,
            sp.partner_id,
            COALESCE(am.name, sm.reference) as document,
            CASE
                WHEN ((sl_src.usage = 'supplier' OR (sl_src.usage = 'transit' AND sl_src.company_id IS NULL)) AND
                      (sl_dest.usage = 'customer' OR (sl_dest.usage = 'transit' AND sl_dest.company_id IS NULL))) THEN 'dropship'
                ELSE COALESCE(svl_in.l10n_ro_valued_type, 'indefinite')
            END as valued_type,
            pt.categ_id as categ_id
                {select}
            from stock_move as sm
                left join stock_picking as sp on sm.picking_id = sp.id
                left join stock_location sl_src ON sp.location_id = sl_src.id
                left join stock_location sl_dest ON sp.location_dest_id = sl_dest.id
                inner join stock_valuation_layer as svl_in
                    on svl_in.stock_move_id = sm.id and
                    (
                     (sm.location_dest_id in %(locations)s and svl_in.quantity>=0 and
                      l10n_ro_valued_type not like '%%_return')
                    or
                     (sm.location_id in %(locations)s and (svl_in.quantity<=0 and
                     l10n_ro_valued_type='reception_return'))
                    or
                     (svl_in.quantity>=0 and
                      ((sl_src.usage = 'supplier' OR (sl_src.usage = 'transit' AND sl_src.company_id IS NULL)) AND
                       (sl_dest.usage = 'customer' OR (sl_dest.usage = 'transit' AND sl_dest.company_id IS NULL))))
                    )
                left join product_product prod on prod.id = sm.product_id
                left join product_template pt on pt.id = prod.product_tmpl_id
                left join account_move am on svl_in.l10n_ro_invoice_id = am.id
            {join}
            where
                sm.state = 'done' AND
                sm.company_id = %(company)s AND
                ( %(all_products)s  or sm.product_id in %(product)s ) AND
                sm.date >= %(datetime_from)s  AND  sm.date <= %(datetime_to)s  AND
                (sm.location_dest_id in %(locations)s or
                 sm.location_id in %(locations)s or
                 ((sl_src.usage = 'supplier' OR (sl_src.usage = 'transit' AND sl_src.company_id IS NULL)) AND
                  (sl_dest.usage = 'customer' OR (sl_dest.usage = 'transit' AND sl_dest.company_id IS NULL))))
            GROUP BY sm.product_id, sm.date,
             sm.reference, sp.partner_id, l10n_ro_account_id,
             svl_in.l10n_ro_invoice_id, am.name, svl_in.l10n_ro_valued_type,
             pt.categ_id, sl_src.usage, sl_src.company_id, sl_dest.usage, sl_dest.company_id {group})
        a
                """
        return sql

    def _get_sql_select_out(self):
        field, select, join, group = self._get_lot_fields()

        sql = f"""
        insert into l10n_ro_stock_storage_sheet_line
          (report_id, product_id, amount_out, quantity_out, unit_price_out,
           account_id, invoice_id, date_time, date, reference,  location_id,
           partner_id, document, valued_type, categ_id {field})

        select * from(

        SELECT  %(report)s as report_id, sm.product_id as product_id,
            -1*COALESCE(sum(svl_out.value),0)   as amount_out,
            -1*COALESCE(ROUND(sum(svl_out.quantity), 5),0) as quantity_out,
            CASE
                WHEN ROUND(COALESCE(sum(svl_out.quantity), 0), 5) != 0
                    THEN COALESCE(sum(svl_out.value),0) / sum(svl_out.quantity)
                ELSE 0
            END as unit_price_out,
            svl_out.l10n_ro_account_id as account_id,
            svl_out.l10n_ro_invoice_id as invoice_id,
            sm.date as date_time,
            date_trunc('day', sm.date at time zone 'utc' at time zone %(tz)s) as date,
            sm.reference as reference,
            %(location)s as location_id,
            sp.partner_id,
            COALESCE(am.name, sm.reference) as document,
            CASE
                WHEN ((sl_src.usage = 'supplier' OR (sl_src.usage = 'transit' AND sl_src.company_id IS NULL)) AND
                      (sl_dest.usage = 'customer' OR (sl_dest.usage = 'transit' AND sl_dest.company_id IS NULL))) THEN 'dropship'
                ELSE COALESCE(svl_out.l10n_ro_valued_type, 'indefinite')
            END as valued_type,
            pt.categ_id as categ_id
            {select}
            from stock_move as sm
                left join stock_picking as sp on sm.picking_id = sp.id
                left join stock_location sl_src ON sp.location_id = sl_src.id
                left join stock_location sl_dest ON sp.location_dest_id = sl_dest.id
                inner join stock_valuation_layer as svl_out
                on svl_out.stock_move_id = sm.id and
                 (
                  (sm.location_id in %(locations)s and svl_out.quantity<=0 and
                    l10n_ro_valued_type != 'reception_return')
                 or
                  (sm.location_dest_id in  %(locations)s and (svl_out.quantity>=0 and
                   l10n_ro_valued_type like '%%_return'))
                 or
                  (svl_out.quantity<=0 and
                   ((sl_src.usage = 'supplier' OR (sl_src.usage = 'transit' AND sl_src.company_id IS NULL)) AND
                    (sl_dest.usage = 'customer' OR (sl_dest.usage = 'transit' AND sl_dest.company_id IS NULL))))
                 )
                left join product_product prod on prod.id = sm.product_id
                left join product_template pt on pt.id = prod.product_tmpl_id
                left join account_move am on svl_out.l10n_ro_invoice_id = am.id
                {join}
            where
                sm.state = 'done' AND
                sm.company_id = %(company)s AND
                ( %(all_products)s  or sm.product_id in %(product)s ) AND
                sm.date >= %(datetime_from)s  AND  sm.date <= %(datetime_to)s  AND
                (sm.location_id in %(locations)s or
                 sm.location_dest_id in %(locations)s or
                 ((sl_src.usage = 'supplier' OR (sl_src.usage = 'transit' AND sl_src.company_id IS NULL)) AND
                  (sl_dest.usage = 'customer' OR (sl_dest.usage = 'transit' AND sl_dest.company_id IS NULL))))
            GROUP BY sm.product_id, sm.date,
                     sm.reference, sp.partner_id, svl_out.l10n_ro_account_id,
                     svl_out.l10n_ro_invoice_id, am.name, svl_out.l10n_ro_valued_type,
                     pt.categ_id, sl_src.usage, sl_src.company_id, sl_dest.usage, sl_dest.company_id {group})
        a
                """
        return sql
