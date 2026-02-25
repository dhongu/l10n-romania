# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "eTransport Batch Enhancement",
    "version": "18.0.0.1.0",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "summary": "eTransport Batch Enhancement",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "l10n_ro_edi",
        "l10n_ro_edi_stock",
        "l10n_ro_edi_stock_batch",
        "l10n_ro_etransport_enhancement",
        "l10n_ro_stock_picking_batch_report",
    ],
    "license": "LGPL-3",
    "price": 25.00,
    "currency": "EUR",
    "data": [
        "views/stock_picking_batch_view.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Mature",
    "maintainers": ["dhongu"],
    "extra_buy": True,
}
