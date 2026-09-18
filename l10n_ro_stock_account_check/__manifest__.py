# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Stock Accounting Check",
    "summary": "Check the stock valuation against the general ledger",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "countries": ["ro"],
    "author": "Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "depends": [
        "l10n_ro_stock_account",
        "purchase_stock",
        "sale_stock",
        # "deltatech_purchase_price",
    ],
    "data": [
        "report/stock_check_report_view.xml",
        "security/ir.model.access.csv",
        "views/stock_view.xml",
    ],
    "installable": True,
    "development_status": "Mature",
    "maintainers": ["dhongu"],
}
