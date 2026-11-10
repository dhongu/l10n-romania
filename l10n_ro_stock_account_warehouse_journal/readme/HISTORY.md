## 20.0.1.1.0 (2026-11-10)

- The module depends on `stock_account` instead of `l10n_ro_stock_account`, so the stock
  journal per warehouse works on the native Odoo stock valuation. The posting of the
  additional entries of `l10n_ro_stock_account` moves to the bridge module
  `l10n_ro_stock_account_warehouse_journal_extra`, installed automatically with both.

## 20.0.1.0.0 (2026-10-14)

- Stock journal per warehouse, brought back from `l10n_ro_stock_account` 18.0
  (`l10n_ro_property_stock_journal_id` on `stock.warehouse`), adapted to the
  Odoo 19+ stock entries: the standard entry, the additional Romanian entries and
  the FIFO negative stock compensation.
