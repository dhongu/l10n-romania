# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api
from odoo.tools import SQL
from odoo.tools.sql import column_exists, table_exists

_logger = logging.getLogger(__name__)


def _migrate_sale_amount(env):
    """18.0 kept the store sale amount on the valuation layer, removed in 19.0."""
    cr = env.cr
    if not (
        table_exists(cr, "stock_valuation_layer")
        and column_exists(cr, "stock_valuation_layer", "l10n_ro_sale_amount")
        and column_exists(cr, "stock_valuation_layer", "stock_move_id")
    ):
        return
    cr.execute(
        SQL(
            """
            UPDATE stock_move sm
               SET l10n_ro_store_sale_amount = svl.amount
              FROM (
                    SELECT stock_move_id, SUM(l10n_ro_sale_amount) AS amount
                      FROM stock_valuation_layer
                     WHERE l10n_ro_sale_amount IS NOT NULL
                       AND l10n_ro_sale_amount != 0
                       AND stock_move_id IS NOT NULL
                  GROUP BY stock_move_id
                   ) svl
             WHERE sm.id = svl.stock_move_id
            """
        )
    )
    _logger.info("Store sale amount migrated on %s stock moves", cr.rowcount)


def _migrate_markup_account(env):
    """18.0 used the price difference account of the category for the markup.

    That account was also used for the purchase price differences (308), so
    only the 378 accounts are carried over.
    """
    cr = env.cr
    column = "property_account_creditor_price_difference_categ"
    if not column_exists(cr, "product_category", column):
        return
    cr.execute(
        SQL(
            "SELECT id, %s FROM product_category WHERE %s IS NOT NULL",
            SQL.identifier(column),
            SQL.identifier(column),
        )
    )
    for categ_id, values in cr.fetchall():
        for company_id, account_id in (values or {}).items():
            company = env["res.company"].browse(int(company_id)).exists()
            account = env["account.account"].with_company(company).browse(account_id)
            if not company or not account.exists():
                continue
            if not (account.code or "").startswith("378"):
                continue
            env["product.category"].with_company(company).browse(
                categ_id
            ).l10n_ro_property_store_markup_account_id = account


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    _migrate_sale_amount(env)
    _migrate_markup_account(env)
