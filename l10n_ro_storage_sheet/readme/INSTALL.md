This module is the successor of the Terrabit copy of `l10n_ro_stock_report`.
It is not installed automatically in its place: the old name now resolves to
the OCA `l10n_ro_stock_report` module, which depends on `l10n_ro_stock_account`.

On a database where the storage sheet was installed without
`l10n_ro_stock_account`, install `l10n_ro_storage_sheet` and uninstall
`l10n_ro_stock_report` before updating, otherwise the update also installs the
OCA stock valuation engine.

The report models are transient, so no data is migrated.
