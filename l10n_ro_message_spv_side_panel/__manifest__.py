# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "SPV Messages Side Panel",
    "version": "19.0.1.3.0",
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",
    "summary": "Split view for the SPV messages: the invoice details in a side panel",
    "countries": ["ro"],
    "category": "Localization",
    "depends": ["l10n_ro_message_spv", "deltatech_web_side_panel"],
    "license": "AGPL-3",
    "support": "support@terrabit.ro",
    "data": [
        "views/spv_document_templates.xml",
        "views/message_spv_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "l10n_ro_message_spv_side_panel/static/src/spv_split.scss",
        ],
    },
    "images": ["static/description/main_screenshot.png"],
    "uninstall_hook": "uninstall_hook",
    "development_status": "Beta",
    "maintainers": ["dhongu"],
}
