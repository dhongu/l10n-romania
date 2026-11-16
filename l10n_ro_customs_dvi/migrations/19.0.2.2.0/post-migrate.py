# ©  2008-2026 Deltatech
# See README.rst file on addons root folder for license details
"""Tipul documentului „Import (DVI)” pe notele DVI-urilor validate înainte de modulul nou."""

from odoo.tools import SQL


def migrate(cr, version):
    cr.execute(
        SQL(
            """
            UPDATE account_move move
               SET l10n_ro_document_type = 'customs_declaration'
              FROM stock_landed_cost cost
             WHERE cost.account_move_id = move.id
               AND cost.landed_type = 'dvi'
            """
        )
    )
