# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Storno Enhancements",
    "summary": "Romania - Storno Enhancements",
    "version": "19.0.0.0.4",
    "author": "Dorin Hongu,Terrabit,Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "depends": ["account", "l10n_ro"],
    "countries": ["ro"],
    "data": ["views/account_account_view.xml", "views/account_move_view.xml"],
    "license": "AGPL-3",
    "maintainers": ["dhongu"],
    "development_status": "Production/Stable",
    "post_init_hook": "post_init_hook",
}
