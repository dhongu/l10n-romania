# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Cash Register",
    "version": "17.0.1.1.6",
    "author": "Terrabit," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Localization",
    "depends": ["account"],
    "countries": ["ro"],
    "data": [
        "views/cash_register_views.xml",
        "security/ir.model.access.csv",
        "security/cash_register_security.xml",
        "wizard/cash_register_operation_view.xml",
        "views/report_cash_register.xml",
        # "views/account_payment_view.xml",
        "data/ir_cron_data.xml",
    ],
    "license": "AGPL-3",
}
