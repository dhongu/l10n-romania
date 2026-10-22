# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - POS Partner e-Factura Check for ANAF customers",
    "summary": "The cashier confirms a customer fetched from ANAF in POS before it goes on the order",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "author": "Dorin Hongu, Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": ["l10n_ro_pos_partner_efactura", "l10n_ro_pos_partner"],
    "data": ["views/res_partner_view.xml"],
    "assets": {
        "point_of_sale._assets_pos": [
            "l10n_ro_pos_partner_efactura_anaf/static/src/**/*",
        ],
    },
    "auto_install": True,
    "development_status": "Beta",
}
