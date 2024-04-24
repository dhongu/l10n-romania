# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return


    cr.execute("DELETE FROM ir_ui_view WHERE arch_db::text LIKE '%l10n_ro_e_invoice%';")
    env = api.Environment(cr, SUPERUSER_ID, {})
    IrModule = env["ir.module.module"]
    IrModule.update_list()

    modules = ["l10n_ro_config", "l10n_ro_partner_create_by_vat", "l10n_ro_account_edi_ubl"]

    for module in modules:

        l10n_ro_stock_account_determination_module = IrModule.search(
            [("name", "=", module)]
        )
        if l10n_ro_stock_account_determination_module.state not in (
            "installed",
            "to install",
            "to upgrade",
        ):
            l10n_ro_stock_account_determination_module.button_install()



