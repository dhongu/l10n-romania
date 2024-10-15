# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Terrabit - Picking Reports",
    "summary": "Rapoarte: NIR, aviz, bon consum",
    "license": "AGPL-3",
    "version": "18.0.1.1.3",
    "author": "Dorin Hongu," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Localization",
    "countries": ["ro"],
    "depends": [
        "base",
        "stock",
        "l10n_ro_config",
        "purchase_stock",
        "sale_stock",
        "l10n_ro_stock",
        # "l10n_ro_stock_account",
    ],
    "data": [
        "views/l10n_ro_stock_picking_report.xml",
        "views/report_picking.xml",
        "views/stock_view.xml",
        # "views/res_config_view.xml",
        "views/stock_location_view.xml",
        "report/stock_picking_cumulative_view.xml",
        "security/ir.model.access.csv",
    ],
}
