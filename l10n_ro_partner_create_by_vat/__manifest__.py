# Copyright  2015 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Romania - Partner Create by VAT",
    "summary": "Romania - Partner Create by VAT",
    "version": "12.0.1.0.0",
    "author": "Forest and Biomass Romania, " "Odoo Community Association (OCA)",
    "website": "http://www.forbiom.eu",
    "category": "Localization",
    "depends": [
        #'l10n_ro',
        "base_vat"
    ],
    "data": ["views/res_partner_view.xml",],
    "installable": True,
    "license": "AGPL-3",
    "application": False,
    "auto_install": False,
}
