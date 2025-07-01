# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "eTransport Enhancement",
    "version": "17.0.0.0.2",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "summary": "eTransport enhancement",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "l10n_ro_edi",
        "l10n_ro_edi_stock",
    ],
    "license": "LGPL-3",
    "price": 25.00,
    "currency": "EUR",
    "data": [
        "views/stock_picking_view.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Mature",
    "maintainers": ["dhongu"],
    "extra_buy": True,
    "post_init_hook": "post_init_hook",
}
