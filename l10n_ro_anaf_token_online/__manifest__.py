# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - ANAF SPV Token for Odoo Online",
    "summary": "e-Factura SPV token through Terrabit, renewed for you, on Odoo Online too (no Python)",
    "license": "AGPL-3",
    "version": "20.0.1.0.0",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["l10n_ro_edi", "deltatech_iap_online"],
    # same token renewed by another channel: the two modules must not be installed together
    "excludes": ["terrabit_iap_anaf"],
    "data": [
        "data/ir_model_fields_data.xml",
        "data/base_automation_data.xml",
        "data/ir_actions_server_data.xml",
        "data/iap_online_service_data.xml",
        "views/res_config_settings_views.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Alpha",
    "consultant_sheet": "full",
    "maintainers": ["dhongu"],
}
