# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - SPV Messages for Odoo Online",
    "summary": "Register of the e-Factura (SPV) messages on Odoo Online too: sent, received, refused (no Python)",
    "license": "AGPL-3",
    "version": "19.0.1.0.1",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["l10n_ro_edi"],
    "excludes": ["l10n_ro_message_spv"],
    "data": [
        "data/ir_model_fields_data.xml",
        "data/ir_actions_server_data.xml",
        "views/l10n_ro_edi_document_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Alpha",
    "consultant_sheet": "simple",
    "maintainers": ["dhongu"],
}
