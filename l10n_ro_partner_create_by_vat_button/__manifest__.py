# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Partner Create by VAT Button",
    "license": "AGPL-3",
    "version": "18.0.1.1.6",
    "author": "Dorin Hongu," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Localization",
    "countries": ["ro"],
    "depends": [
        "l10n_ro_config",
        "l10n_ro_partner_create_by_vat",
        # "l10n_ro_partner_create_by_vat_openapi"
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/get_data_form_view.xml",
        "views/res_partner_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "sequence": 100,
}
