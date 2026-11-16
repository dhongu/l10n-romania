# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Picking Reports for Odoo Online",
    "summary": "NIR, delivery note (aviz) and consumption voucher, Romanian layout, on Odoo Online too (no Python)",
    "license": "AGPL-3",
    "version": "19.0.1.0.1",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["purchase_stock", "sale_stock", "l10n_ro_invoice_report_online"],
    # same documents from other fields: the two modules must not be installed together
    "excludes": ["l10n_ro_picking_report"],
    "data": [
        "data/ir_model_fields_data.xml",
        "data/base_automation_data.xml",
        "views/report_actions.xml",
        "views/report_picking.xml",
        "views/stock_picking_views.xml",
        "views/stock_location_views.xml",
        "views/res_company_views.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Beta",
    "consultant_sheet": "full",
    "maintainers": ["dhongu"],
}
