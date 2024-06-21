# © 2008-2016 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Currency Rate Update",
    "version": "12.0.1.0.1",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "http://camptocamp.com",
    "license": "AGPL-3",
    "category": "Financial Management/Configuration",
    "depends": [
        "base",
        "account",
    ],  # Added to ensure account security groups are present
    "external_dependencies": {
        "python": [
            "future",
        ],
    },
    "data": [
        "data/cron.xml",
        "views/currency_rate_update.xml",
        # "views/account_config_settings.xml",
        "security/rule.xml",
        "security/ir.model.access.csv",
        "views/res_currency_view.xml",
    ],
    "installable": True,
}
