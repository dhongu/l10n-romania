# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Stock Accounting Store",
    "version": "20.0.1.1.0",
    "category": "Localization",
    "countries": ["ro"],
    "summary": "Romania - Stock Accounting Store",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "depends": ["l10n_ro_stock_account"],
    "license": "AGPL-3",
    "data": [
        "security/ir.access.csv",
        "data/ir_sequence.xml",
        "views/product_category_view.xml",
        "views/stock_location_view.xml",
        "views/stock_move_view.xml",
        "views/store_revaluation_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "development_status": "Mature",
    "maintainers": ["dhongu"],
    "images": ["static/description/main_screenshot.png"],
}
