# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Stock Journal per Warehouse",
    "summary": "Post the stock journal entries of each warehouse in its own journal",
    "images": ["static/description/main_screenshot.png"],
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "countries": ["ro"],
    "author": "Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "depends": [
        "l10n_ro_stock_account",
    ],
    "data": [
        "views/stock_warehouse_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["dhongu"],
}
