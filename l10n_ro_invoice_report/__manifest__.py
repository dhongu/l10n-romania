# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Invoice Report Terrabit",
    "summary": "Localizare Terrabit",
    "version": "16.0.3.1.1",
    "author": "Dorin Hongu," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": [
        "base",
        "account",
        "l10n_ro_config",
        "purchase",
        "sale",
        # "deltatech_watermark"
    ],
    "data": [
        "views/invoice_report.xml",
        "views/voucher_report.xml",
        "views/payment_report.xml",
        # 'views/account_invoice_view.xml',
        "views/account_voucher_report.xml",
        "views/account_bank_statement_view.xml",
        "views/statement_report.xml",
        "views/res_config_view.xml",
        # 'views/res_partner_view.xml',
    ],
}
