# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Partner Create by VAT Button",
    "license": "AGPL-3",
    "version": "16.0.1.1.0",
    "author": "Dorin Hongu," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Localization",
    "depends": [
        "l10n_ro_config",
        "l10n_ro_partner_create_by_vat",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/get_data_form_view.xml",
        "views/res_partner_view.xml",
    ],
}
