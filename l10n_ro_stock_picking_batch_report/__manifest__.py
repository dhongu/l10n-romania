# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Terrabit - Picking batch Report",
    "summary": "Rapoarte din batch: aviz",
    "license": "AGPL-3",
    "version": "18.0.0.0.1",
    "author": "Dan Stoica," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Localization",
    "countries": ["ro"],
    "depends": [
        "l10n_ro_stock_picking_report",
        "stock_picking_batch",
    ],
    "excludes": ["l10n_ro_stock_picking_comment_template"],
    "data": [
        "views/l10n_ro_batch_report.xml",
    ],
}
