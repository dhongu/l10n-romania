# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Invoice Report Terrabit",
    "summary": "Localizare Terrabit - Facturi, Chitanta",
    "version": "19.0.3.4.20",
    "author": "Dorin Hongu,Terrabit,Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "license": "AGPL-3",
    "category": "Localization",
    "development_status": "Mature",
    "countries": ["ro"],
    "depends": [
        "base",
        "account",
        "l10n_ro_report_common",
        "purchase",
        "sale",
        "stock_delivery",
    ],
    "data": [
        "views/invoice_report.xml",
        "views/payment_report.xml",
        "views/account_invoice_view.xml",
        "views/account_voucher_report.xml",
        "views/account_bank_statement_view.xml",
        # "views/statement_report.xml",
        "views/res_config_view.xml",
        "views/account_journal_view.xml",
        "views/res_partner_view.xml",
    ],
}
