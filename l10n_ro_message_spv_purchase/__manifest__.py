# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Purchase Message SPV",
    "version": "18.0.0.0.3",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "summary": "Add SPV message on purchase orders for Romania",
    "countries": ["ro"],
    "category": "Localization",
    "depends": ["l10n_ro_message_spv", "purchase"],
    "license": "LGPL-3",
    "price": 25.00,
    "currency": "EUR",
    "data": [
        "views/message_spv_view.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Beta",
    "maintainers": ["dhongu"],
    "extra_buy": True,
}
