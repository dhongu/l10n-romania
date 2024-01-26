# Copyright  2015 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Romania - Partner Create by VAT",
    "summary": "Romania - Partner Create by VAT",
    "version": "15.0.1.0.0",
    "author": "Forest and Biomass Romania, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Localization",
    "depends": [
        #'l10n_ro',
        "base_vat",
        "l10n_ro_config",
    ],
    "data": [
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "application": False,
    "auto_install": False,
}
