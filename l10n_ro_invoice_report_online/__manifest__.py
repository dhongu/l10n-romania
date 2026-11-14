# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Invoice Report for Odoo Online",
    "summary": "Romanian invoice and receipt (chitanta) layout, on Odoo Online too (no Python)",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["account", "base_automation", "l10n_ro_report_common_online"],
    # same data in other fields: the two modules must not be installed together
    "excludes": ["l10n_ro_invoice_report"],
    "data": [
        "data/ir_model_fields_data.xml",
        "data/base_automation_data.xml",
        "views/invoice_report.xml",
        "views/payment_report.xml",
        "views/account_voucher_report.xml",
        "views/account_move_views.xml",
        "views/account_journal_views.xml",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Beta",
    "consultant_sheet": "full",
    "maintainers": ["dhongu"],
}
