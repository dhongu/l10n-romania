# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Picking Reports",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "author": "Dorin Hongu," "Odoo Community Association (OCA)",
    "category": "Generic Modules",
    "depends": [
        "base",
        "stock",
        "l10n_ro_config",
        "purchase_stock",
        "sale_stock",
        "l10n_ro_stock",
        # 'l10n_ro_stock_account'
    ],
    "data": ["views/l10n_ro_stock_picking_report.xml", "views/report_picking.xml", "views/stock_view.xml"],
}
