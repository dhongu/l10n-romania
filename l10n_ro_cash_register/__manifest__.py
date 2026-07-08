# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Cash Register",
    "version": "19.0.1.1.8",
    "summary": "Romania - Cash Register",
    "author": "Terrabit,Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "depends": ["account", "l10n_ro_account_sequence"],
    "countries": ["ro"],
    "development_status": "Mature",
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
