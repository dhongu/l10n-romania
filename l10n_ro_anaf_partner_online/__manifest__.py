# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - ANAF Partner Data for Odoo Online",
    "summary": "Fill in Romanian partners from ANAF by their CUI, on Odoo Online too (no Python, service by Terrabit)",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["deltatech_iap_online", "contacts"],
    "data": [
        "data/ir_model_data.xml",
        "security/ir.model.access.csv",
        "data/ir_actions_server_data.xml",
        "data/iap_online_service_data.xml",
        "views/res_partner_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "l10n_ro_anaf_partner_online/static/src/js/anaf_lookup_widget.esm.js",
            "l10n_ro_anaf_partner_online/static/src/xml/anaf_lookup_widget.xml",
        ],
    },
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Alpha",
    "maintainers": ["dhongu"],
}
