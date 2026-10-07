# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

from odoo.tools import SQL

_logger = logging.getLogger(__name__)

OLD_MODULE = "l10n_ro_account_storno"
NEW_MODULE = "l10n_ro_storno_enhancement"
MIGRATED_PARAM = "l10n_ro_storno_enhancement.migrated_from_account_storno"


def pre_init_hook(env):
    """Take over the records of the former l10n_ro_account_storno module.

    The module was renamed because the technical name is already registered
    on Odoo Apps by another publisher. When the old module is installed, its
    fields, views and data are moved to the new name before the new module
    loads, so nothing is duplicated and the account usage values are kept.
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

    cr.execute(SQL("UPDATE ir_model_data SET module = %s WHERE module = %s", NEW_MODULE, OLD_MODULE))
    cr.execute(SQL("UPDATE ir_model_constraint SET module = %s WHERE module = %s", new_id, old_id))
    cr.execute(SQL("UPDATE ir_model_relation SET module = %s WHERE module = %s", new_id, old_id))
    # modules that still depend on the old name now point to the new one
    cr.execute(
        SQL(
            "UPDATE ir_module_module_dependency SET name = %s WHERE name = %s AND module_id != %s",
            NEW_MODULE,
            OLD_MODULE,
            new_id,
        )
    )
    cr.execute(
        SQL(
            "UPDATE ir_module_module SET state = 'uninstalled', latest_version = NULL WHERE id = %s",
            old_id,
        )
    )
    env["ir.config_parameter"].sudo().set_param(MIGRATED_PARAM, "1")


def post_init_hook(env):
    params = env["ir.config_parameter"].sudo()
    if params.get_param(MIGRATED_PARAM):
        # keep the account usage values set while the old module was installed
        params.search([("key", "=", MIGRATED_PARAM)]).unlink()
        return
    env["res.company"]._l10n_ro_initialize_accounts()
