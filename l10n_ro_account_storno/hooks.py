# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


def post_init_hook(env):
    env["res.company"]._l10n_ro_initialize_accounts()
