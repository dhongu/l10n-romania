# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Report Common for Odoo Online",
    "summary": "Romanian report header blocks and RON amounts in words, on Odoo Online too (no Python)",
    "license": "LGPL-3",
    "version": "19.0.1.0.2",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["l10n_ro"],
    "excludes": ["l10n_ro_report_common"],
    "data": [
        "data/ir_model_fields_data.xml",
        "views/report_templates.xml",
        "views/res_company_views.xml",
        "views/res_partner_bank_views.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Beta",
    "consultant_sheet": "simple",
    "maintainers": ["dhongu"],
}
