Fields of the OCA `l10n_ro_stock_account` module, without its logic. It keeps the
columns and the data of a database that had the OCA module, so that the OCA
module can be removed and the data migrated to the next version.

The company accounts used by the stock accounting, defined in the OCA `l10n_ro_config`
(picking payable and receivable, usage giving, stock transfer, not eligible tax), are
included too, so that `l10n_ro_config` can be removed.

It depends on `l10n_ro_stock_base`, the replacement of the OCA `l10n_ro_stock`, like the OCA module depends on `l10n_ro_stock`.

It adds no behavior: the computed fields of the OCA module (`l10n_ro_move_type`,
`l10n_ro_account_id`, `l10n_ro_transfer_account_id`, `fifo_per_location`,
`fifo_location_negative_compensation`) are plain stored fields here, so they are
not filled for new records. It has no views and no dependency on the
`l10n.ro.mixin`.
