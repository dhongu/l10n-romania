# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from . import models


def uninstall_hook(env):
    """The menus of the SPV messages open the original action again."""
    action = env.ref("l10n_ro_message_spv.action_l10n_ro_message_spv", raise_if_not_found=False)
    if not action:
        return
    for xmlid in ("menu_l10n_ro_spv", "menu_l10n_ro_message_spv"):
        menu = env.ref(f"l10n_ro_message_spv.{xmlid}", raise_if_not_found=False)
        if menu:
            menu.action = f"ir.actions.act_window,{action.id}"
