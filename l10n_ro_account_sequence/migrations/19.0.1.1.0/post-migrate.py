# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""Tipul documentului pe notele plăților prin casă înregistrate înainte de modulul nou."""

from odoo.tools import SQL


def migrate(cr, version):
    cr.execute(
        SQL(
            """
            UPDATE account_move
               SET l10n_ro_document_type = l10n_ro_cash_document_type
             WHERE move_type = 'entry'
               AND l10n_ro_cash_document_type IN %s
            """,
            ("customer_receipt", "supplier_receipt", "payment_disposal", "cash_collection"),
        )
    )
