from . import report
from . import wizards
from . import models

from odoo import api, SUPERUSER_ID


def _set_account_group(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    account_group = env["account.group"].search([])

    for group in account_group:
        if not group.group_child_ids and not group.account_ids:
            account_ids = env["account.account"].search(
                [("code", "=like", group.code_prefix + "%")]
            )
            account_ids.write({"group_id": group.id})
