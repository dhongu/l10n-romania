# ©  2008-2026 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

from odoo.tools import SQL

_logger = logging.getLogger(__name__)

# Numele vechi al modulului, înainte de alinierea la convenţia `l10n_ro_`.
# `l10n_ro_dvi` nu putea fi folosit — e numele modulului OCA, cu care ne excludem reciproc.
OLD_MODULE = "terrabit_dvi"
NEW_MODULE = "l10n_ro_customs_dvi"


def pre_init_hook(env):
    """Preia înregistrările modulului redenumit, înainte de încărcarea datelor.

    Rulează doar la instalare. Pe o bază unde `terrabit_dvi` era instalat, XML id-urile
    (view-uri, acţiuni, meniu, ACL) aparţin încă vechiului modul. Fără mutarea lor,
    încărcarea datelor modulului nou ar CREA duplicate în loc să actualizeze — adică două
    acţiuni şi două meniuri „DVI" vizibile în interfaţă.

    Se mută **doar** `ir_model_data`, nu şi `ir_module_module.name`: modulul vechi rămâne ca
    stub tranzitoriu (`depends: ["l10n_ro_customs_dvi"]`), ca manifestele clienţilor care îl
    declară ca dependenţă să continue să se încarce, deci are nevoie de rândul lui.

    Pe o instalare curată nu găseşte nimic şi nu face nimic.
    """
    env.cr.execute(
        SQL(
            """
            UPDATE ir_model_data d
               SET module = %(new)s
             WHERE d.module = %(old)s
               AND NOT EXISTS (
                     SELECT 1
                       FROM ir_model_data existing
                      WHERE existing.module = %(new)s
                        AND existing.name = d.name
                   )
            """,
            old=OLD_MODULE,
            new=NEW_MODULE,
        )
    )
    moved = env.cr.rowcount
    if moved:
        _logger.info(
            "%s: preluate %s înregistrări ir_model_data de la %s",
            NEW_MODULE,
            moved,
            OLD_MODULE,
        )
