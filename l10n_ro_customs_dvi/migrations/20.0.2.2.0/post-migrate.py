# ©  2008-2026 Deltatech
# See README.rst file on addons root folder for license details
"""Notele DVI validate înainte de forward-port-ul din 19.0.2.2.0.

- furnizorul extern pe antetul notelor DVI din 2026 validate fără partener (doar antetul, pentru
  jurnalul de TVA pentru cumpărări; notele din perioadele blocate rămân neatinse);
- tipul documentului „Import (DVI)” pe notele DVI.

Ambele sunt idempotente: pe o bază venită din 19.0.2.2.0 nu mai găsesc nimic de schimbat.
"""

from odoo import SUPERUSER_ID, api, fields
from odoo.tools import SQL


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    costs = env["stock.landed.cost"].search(
        [
            ("state", "=", "done"),
            ("vendor_bill_id", "!=", False),
            ("account_move_id", "!=", False),
            ("account_move_id.partner_id", "=", False),
            ("account_move_id.date", ">=", fields.Date.to_date("2026-01-01")),
        ]
    )
    costs = costs.filtered(
        lambda c: not c.company_id._get_violated_lock_dates(c.account_move_id.date, True, c.account_move_id.journal_id)
    )
    costs._set_dvi_move_partner()

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
