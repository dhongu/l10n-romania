# Copyright  2018 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Romania - Account Trial Balance Report",
    "summary": "Romania - Account Trial Balance Report",
    "version": "15.0.1.0.0",
    "category": "Localization",
    "author": "NextERP,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "license": "AGPL-3",
    "depends": [
        "account",
        # "report_xlsx",
        # 'account_financial_report',
        "l10n_ro",
    ],
    "data": [
        # "views/account_view.xml",
        "views/layouts.xml",
        "views/report_template.xml",
        "views/report_trial_balance.xml",
        "views/trial_balance.xml",
        "views/trial_balance_view.xml",
        "wizards/trial_balance_wizard_view.xml",
        "security/ir.model.access.csv",
        # "data/account_group.xml",
    ],
    "qweb": ["static/src/xml/trial_balance_report_template.xml"],
}
