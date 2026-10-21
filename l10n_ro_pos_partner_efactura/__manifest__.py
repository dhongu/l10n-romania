# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - POS Partner e-Factura Check",
    "summary": "Require the partner data needed by e-Factura (SPV) when a customer is created in POS",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["point_of_sale", "l10n_ro_edi"],
    "data": ["views/res_partner_view.xml"],
    "assets": {
        "point_of_sale._assets_pos": [
            "l10n_ro_pos_partner_efactura/static/src/**/*",
        ],
    },
    "development_status": "Beta",
}
