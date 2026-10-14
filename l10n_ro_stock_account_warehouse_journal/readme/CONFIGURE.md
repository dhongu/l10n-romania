1. Create a *Miscellaneous* journal for each warehouse that needs its own stock journal.
2. In *Inventory > Configuration > Warehouses*, open the warehouse and set **Stock Journal**.

**Migration from 18.0.** Install this module in the same run as the
migration of `l10n_ro_stock_account` (or before it): otherwise the update of
`l10n_ro_stock_account` drops the column and the journals set in 18.0 have to
be filled in again on the warehouses.
