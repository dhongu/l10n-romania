# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tools import SQL

_logger = logging.getLogger(__name__)

OLD_MODULE = "l10n_ro_stock_age_report"
NEW_MODULE = "l10n_ro_stock_aged_report"


def pre_init_hook(env):
    """Take over the records of the former l10n_ro_stock_age_report module.

    The module was renamed because the technical name is already registered
    on Odoo Apps by another publisher. When the old module is installed, its
    fields, views, actions and menus are moved to the new name before the new
    module loads, so nothing is duplicated and the last in/out dates on the
    quants are kept. The former module is then removed from the module list.
    """
    cr = env.cr
    cr.execute(
        SQL(
            "SELECT id FROM ir_module_module WHERE name = %s AND state IN ('installed', 'to upgrade', 'to remove')",
            OLD_MODULE,
        )
    )
    old = cr.fetchone()
    if not old:
        return
    cr.execute(SQL("SELECT id FROM ir_module_module WHERE name = %s", NEW_MODULE))
    new = cr.fetchone()
    old_id, new_id = old[0], new[0]
    _logger.info("Migrating module %s to %s", OLD_MODULE, NEW_MODULE)

    # same steps as merge_module() from odoo upgrade-util, without the external dependency
    cr.execute(SQL("UPDATE ir_model_constraint SET module = %s WHERE module = %s", new_id, old_id))
    cr.execute(SQL("UPDATE ir_model_relation SET module = %s WHERE module = %s", new_id, old_id))
    cr.execute(SQL("UPDATE ir_model_data SET module = %s WHERE module = %s", NEW_MODULE, OLD_MODULE))
    cr.execute(
        SQL(
            "UPDATE ir_ui_view SET key = concat(%s::text, right(key, -length(%s))) WHERE key LIKE %s",
            NEW_MODULE,
            OLD_MODULE,
            OLD_MODULE.replace("_", r"\_") + ".%",
        )
    )
    # modules that still depend on the old name now depend on the new one
    cr.execute(
        SQL(
            """
            UPDATE ir_module_module_dependency d
               SET name = %s
              FROM ir_module_module m
             WHERE m.id = d.module_id
               AND d.name = %s
               AND m.name != %s
               AND NOT EXISTS (SELECT 1
                                 FROM ir_module_module_dependency o
                                WHERE o.module_id = d.module_id
                                  AND o.name = %s)
            """,
            NEW_MODULE,
            OLD_MODULE,
            NEW_MODULE,
            NEW_MODULE,
        )
    )
    # remove the former module completely
    cr.execute(SQL("DELETE FROM ir_module_module_dependency WHERE name = %s", OLD_MODULE))
    cr.execute(SQL("DELETE FROM ir_model_data WHERE model = 'ir.module.module' AND res_id = %s", old_id))
    cr.execute(SQL("DELETE FROM ir_module_module WHERE id = %s", old_id))


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
