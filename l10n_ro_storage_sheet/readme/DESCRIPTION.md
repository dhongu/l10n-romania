This module adds the Romanian storage sheet (Fișă Magazie) report: opening
balance, receipts, deliveries and closing balance per product and location,
as a PDF or as a pivot analysis.

It works on the native Odoo stock valuation and does not depend on the
`l10n_ro_stock_account` valuation engine.

It was previously published in this repository as `l10n_ro_stock_report`,
which clashed with the OCA module of the same name. Databases that need the
valued move types of the OCA engine keep using the OCA `l10n_ro_stock_report`.
