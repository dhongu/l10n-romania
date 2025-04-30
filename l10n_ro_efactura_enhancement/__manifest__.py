# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "eFactura Enhacement",
    "version": "17.0.0.0.7",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "summary": "eFactura Enhacement",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "l10n_ro_edi",
        "l10n_ro_efactura",
    ],
    "license": "LGPL-3",
    "price": 25.00,
    "currency": "EUR",
    "data": [
        "data/ir_config_parameter.xml",
        "wizard/account_move_send_views.xml",
        "data/ir_cron.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Mature",
    "maintainers": ["dhongu"],
    "extra_buy": True,
}
