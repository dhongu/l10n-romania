# ©  2008-2026 Deltatech
# See README.rst file on addons root folder for license details
"""Furnizorul extern pe notele DVI din 2026 validate fără partener.

Doar antetul notei, pentru jurnalul de TVA pentru cumpărări; notele din perioadele blocate rămân
neatinse.
"""

from odoo import SUPERUSER_ID, api, fields


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
