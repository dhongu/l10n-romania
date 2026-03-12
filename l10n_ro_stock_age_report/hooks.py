# Part of Odoo. See LICENSE file for full copyright and licensing details.


def post_init_hook(env):
    """
    Update existing stock.quant records with last in/out dates based on stock moves.
    """
    cr = env.cr

    # Update last in date based on latest 'done' stock move where destination is the quant location
    # for quants that have no last in date yet.
    # We use subqueries for better performance on large datasets.

    query_in = """
        UPDATE stock_quant sq
        SET l10n_ro_last_in_date = last_in.max_date
        FROM (
            SELECT sm.product_id, sm.location_dest_id, MAX(sm.date) as max_date
            FROM stock_move sm
            WHERE sm.state = 'done'
              AND sm.location_dest_id IS NOT NULL
            GROUP BY sm.product_id, sm.location_dest_id
        ) AS last_in
        WHERE sq.product_id = last_in.product_id
          AND sq.location_id = last_in.location_dest_id
          AND sq.l10n_ro_last_in_date IS NULL
          AND sq.quantity > 0;
    """
    cr.execute(query_in)

    # Update last out date based on latest 'done' stock move where source is the quant location
    # for quants that have no last out date yet.

    query_out = """
        UPDATE stock_quant sq
        SET l10n_ro_last_out_date = last_out.max_date
        FROM (
            SELECT sm.product_id, sm.location_id, MAX(sm.date) as max_date
            FROM stock_move sm
            WHERE sm.state = 'done'
              AND sm.location_id IS NOT NULL
            GROUP BY sm.product_id, sm.location_id
        ) AS last_out
        WHERE sq.product_id = last_out.product_id
          AND sq.location_id = last_out.location_id
          AND sq.l10n_ro_last_out_date IS NULL
          AND sq.quantity > 0;
    """
    cr.execute(query_out)
