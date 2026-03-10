# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "eFactura Enhancement",
    "version": "18.0.0.1.13",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "summary": "eFactura Enhancement",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "l10n_ro_edi",
        "l10n_ro_config",
        "account_edi_ubl_cii",
        # "l10n_ro_efactura",
    ],
    "license": "LGPL-3",
    "price": 25.00,
    "currency": "EUR",
    "data": [
        "data/ir_config_parameter.xml",
        # "wizard/account_move_send_views.xml",
        "data/ir_cron.xml",
        "views/account_move.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Mature",
    "maintainers": ["dhongu"],
    "extra_buy": True,
}
