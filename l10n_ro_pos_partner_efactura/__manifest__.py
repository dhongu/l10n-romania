# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - POS Partner e-Factura Check",
    "summary": "Customer by CUI from ANAF at the till, with the data e-Factura (SPV) needs",
    "license": "AGPL-3",
    "version": "19.0.1.1.2",
    "images": ["static/description/main_screenshot.png"],
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["point_of_sale", "l10n_ro_edi", "l10n_ro_anaf_partner_lookup"],
    # The same search by CUI at the till, from OCA: two ANAF buttons would be one too many
    "excludes": ["l10n_ro_pos_partner"],
    "data": ["views/res_partner_view.xml"],
    "assets": {
        "point_of_sale._assets_pos": [
            "l10n_ro_pos_partner_efactura/static/src/**/*",
        ],
    },
    "development_status": "Beta",
}
