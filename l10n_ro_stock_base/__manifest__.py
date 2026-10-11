# Copyright (C) 2019 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Romania - Stock Base",
    "summary": "Consume and usage giving locations and operations, net weight",
    "license": "AGPL-3",
    "countries": ["ro"],
    "version": "19.0.0.0.1",
    "category": "Localization",
    "author": "Terrabit, Dorin Hongu",
    "maintainers": ["dhongu"],
    "website": "https://www.terrabit.ro",
    "depends": ["stock"],
    "data": [
        "data/stock_data.xml",
        "views/stock_warehouse_view.xml",
        "views/product_template_view.xml",
    ],
    "installable": True,
    "development_status": "Beta",
}
