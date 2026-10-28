# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools import SQL

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Redenumește numerele de registru duplicate înainte de crearea indexului unic.

    Indexul `l10n_ro_cash_register_unique_name` pe (name, journal_id) nu se poate crea
    dacă baza conține deja registre cu același număr pe aceeași casierie (numerotare
    dublă din versiunile fără index). În fiecare grup de dubluri, registrul cu cea mai
    veche dată își păstrează numărul; celelalte primesc sufixul datei, de exemplu
    `CSH000000001/2025-01-04`. Sufixul este unic pe casierie, datorită constrângerii
    existente unique(date, journal_id).
    """
    cr.execute(
        SQL(
            """
            WITH ranked AS (
                SELECT id, name, date,
                       row_number() OVER (PARTITION BY journal_id, name ORDER BY date, id) AS rn
                  FROM l10n_ro_cash_register
                 WHERE name IS NOT NULL AND name NOT IN ('/', '')
            )
            UPDATE l10n_ro_cash_register r
               SET name = ranked.name || '/' || to_char(ranked.date, 'YYYY-MM-DD')
              FROM ranked
             WHERE r.id = ranked.id AND ranked.rn > 1
         RETURNING r.id, ranked.name, r.name
            """
        )
    )
    for register_id, old_name, new_name in cr.fetchall():
        _logger.warning(
            "l10n_ro_cash_register: registrul %s cu număr duplicat %s a fost redenumit %s",
            register_id,
            old_name,
            new_name,
        )
