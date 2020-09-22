# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Romania - Invoice Report",
    "version": "13.0.2.0.2",
    "author": "Dorin Hongu," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": ["base", "account", "l10n_ro_config", "deltatech_watermark"],
    "data": [
        "views/invoice_report.xml",
        "views/voucher_report.xml",
        "views/payment_report.xml",
        # 'views/account_invoice_view.xml',
        "views/account_voucher_report.xml",
        "views/account_bank_statement_view.xml",
        "views/statement_report.xml",
        # 'views/res_partner_view.xml',
    ],
}
