# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - SPV Messages Side Panel for Odoo Online",
    "summary": "Split view for the SPV messages on Odoo Online: the invoice read from its XML in a side panel (no Python)",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["l10n_ro_message_spv_online", "deltatech_web_side_panel"],
    # same split view on the model of the OCA module: the two modules must not be installed together
    "excludes": ["l10n_ro_message_spv_side_panel"],
    "data": [
        "views/l10n_ro_edi_document_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "l10n_ro_message_spv_side_panel_online/static/src/**/*",
        ],
        "web.assets_unit_tests": [
            "l10n_ro_message_spv_side_panel_online/static/tests/**/*",
        ],
    },
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Alpha",
    "consultant_sheet": "simple",
    "maintainers": ["dhongu"],
}
