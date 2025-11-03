# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Partner Create by VAT Button",
    "summary": "Partner Create by VAT Button",
    "license": "AGPL-3",
    "version": "19.0.1.1.5",
    "author": "Dorin Hongu, Terrabit, Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": [
        "l10n_ro_config",
        "l10n_ro_partner_create_by_vat",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/get_data_form_view.xml",
        "views/res_partner_view.xml",
    ],
    "sequence": 100,
    "development_status": "Mature",
}
