# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Stock Accounting Notice",
    "version": "19.0.1.0.0",
    "category": "Localization",
    "countries": ["ro"],
    "summary": "Romania - Default notice (aviz) on picking operation types",
    "author": "Terrabit, NextERP Romania, Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "depends": ["l10n_ro_stock_account_base"],
    "license": "AGPL-3",
    "data": [
        "views/stock_picking_type_view.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Beta",
    "installable": True,
    "auto_install": False,
    "maintainers": ["feketemihai", "mcojocaru", "dhongu"],
}
