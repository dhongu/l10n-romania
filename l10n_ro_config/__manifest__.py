# ©  2015 Forest and Biomass Services Romania
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Localization Config",
    "summary": "Romania - Localization Install and Config Applications",
    "version": "12.0.1.0.0",
    "category": "Localization",
    "author": "Forest and Biomass Services Romania, " "Terrabit, " "Odoo Community Association (OCA)",
    "website": "https://www.forbiom.eu",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["l10n_ro", "base", "sale", "account"],  # pentru ce ?
    "data": [
        "views/res_config_view.xml",
        "views/res_bank_view.xml",
        "data/res_currency_data.xml",
        # 'views/company_view.xml',
        "views/common_report.xml",
    ],
    "images": [],
    "auto_install": False,
    "post_init_hook": "_create_unaccent",
}
