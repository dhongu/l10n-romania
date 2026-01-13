# ©  2008-2022 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Picking Reports -Product Expiry",
    "summary": "Adds product expiry date to picking reports",
    "license": "AGPL-3",
    "version": "19.0.1.0.1",
    "author": "Terrabit,Dorin Hongu,Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["l10n_ro_stock_picking_report", "product_expiry"],
    "data": [
        "views/report_picking.xml",
    ],
    "auto_install": True,
    "development_status": "Mature",
}
