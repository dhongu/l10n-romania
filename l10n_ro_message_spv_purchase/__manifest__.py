# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Purchase Message SPV",
    "version": "19.0.0.0.1",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "summary": "Add SPV message on purchase orders for Romania",
    "countries": ["ro"],
    "category": "Localization",
    "depends": ["l10n_ro_message_spv", "purchase"],
    "license": "AGPL-3",
    "support": "support@terrabit.ro",
    "data": [
        "views/message_spv_view.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "test": ["tests/test_message_spv_purchase.py"],
    "development_status": "Production/Stable",
    "maintainers": ["dhongu"],
    "extra_buy": True,
}
