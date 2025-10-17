# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Romania - Coduri Postale",
    "summary": "Romania - Coduri Postale",
    "countries": ["ro"],
    "license": "AGPL-3",
    "version": "17.0.0.0.0",
    "author": "Terrabit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Localization",
    "depends": ["base_address_extended", "l10n_ro_city"],
    "data": [
        'views/res_partner_view.xml',
        'views/res_zip_view.xml',
        "security/ir.model.access.csv",
    ],
    "development_status": "Beta",
    "installable": True,
    "maintainers": ["dhongu"],
    "post_init_hook": "post_init_hook",

}
