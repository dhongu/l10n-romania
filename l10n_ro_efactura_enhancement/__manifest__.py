# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "eFactura Enhancement",
    "version": "19.0.0.0.11",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "summary": "eFactura Enhancement",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "l10n_ro_edi",
        # "l10n_ro_efactura",
    ],
    "license": "OPL-1",
    "data": [
        "data/ir_config_parameter.xml",
        # "wizard/account_move_send_views.xml",
        "data/ir_cron.xml",
        "views/account_move.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    # "price": 25.00,
    # "currency": "EUR",
    # "support": "odoo@terrabit.ro",
    "development_status": "Mature",
    "maintainers": ["dhongu"],
    "extra_buy": True,
}
