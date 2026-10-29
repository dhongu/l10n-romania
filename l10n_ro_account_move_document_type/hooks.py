# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools import SQL
from odoo.tools.sql import column_exists, create_column

from .models.account_move import JOURNAL_TYPE_DOCUMENT_TYPE, MOVE_TYPE_DOCUMENT_TYPE


def pre_init_hook(env):
    """Creează și completează coloana `l10n_ro_document_type` în SQL, înainte de instalare.

    Cu coloana deja existentă, ORM-ul nu mai recalculează câmpul în Python pentru toate notele,
    ceea ce pe o bază mare ar dura mult. Regulile sunt cele din `_l10n_ro_get_document_type`.
    """
    cr = env.cr
    if column_exists(cr, "account_move", "l10n_ro_document_type"):
        return
    create_column(cr, "account_move", "l10n_ro_document_type", "varchar")
    move_type_cases = SQL(" ").join(
        SQL("WHEN %s THEN %s", move_type, doc_type) for move_type, doc_type in MOVE_TYPE_DOCUMENT_TYPE.items()
    )
    journal_type_cases = SQL(" ").join(
        SQL("WHEN %s THEN %s", journal_type, doc_type) for journal_type, doc_type in JOURNAL_TYPE_DOCUMENT_TYPE.items()
    )
    cr.execute(
        SQL(
            """
            UPDATE account_move move
               SET l10n_ro_document_type = CASE
                   WHEN move.move_type != 'entry' THEN CASE move.move_type %(move_type_cases)s END
                   WHEN move.origin_payment_id IS NOT NULL OR move.statement_line_id IS NOT NULL
                   THEN COALESCE(CASE journal.type %(journal_type_cases)s END, 'journal_entry')
                   ELSE 'journal_entry'
               END
              FROM account_journal journal
             WHERE journal.id = move.journal_id
            """,
            move_type_cases=move_type_cases,
            journal_type_cases=journal_type_cases,
        )
    )
