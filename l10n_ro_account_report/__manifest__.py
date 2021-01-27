# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Account Reports",
    "version": "1.0",
    "author": "Dorin Hongu",
    "website": "",
    "category": "Romania Adaptation",
    "depends": ["account", "date_range",],
    "description": """
Romania  - Accounting Reports
------------------------------------------


    """,
    "data": [
        "views/account_report.xml",
        "views/report_bank_statement.xml",
        "views/report_sale_purchase_journal.xml",
        "views/activity_statement.xml",
        "wizard/account_report_sale_purchase_journal_view.xml",
        "wizard/statement_wizard.xml",
    ],
    "installable": True,
    "auto_install": False,
}
