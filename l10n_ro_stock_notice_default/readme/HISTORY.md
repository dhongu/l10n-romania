## 20.0.1.0.1

- Renamed from `l10n_ro_stock_account_notice` to `l10n_ro_stock_notice_default`. On the
  18.0 → 19.0 upgrade, the OCA `l10n_ro_stock_account` end-migration 19.0.0.1.0 uninstalls
  any module named `l10n_ro_stock_account_notice` (the 18.0 OCA module merged into it), and
  with it every module depending on it.

## 19.0.1.0.0

- Reduced to the default notice flag on operation types: the rest of the notice
  logic is now in `l10n_ro_stock_account_base`.

- Fix: the default notice flag is also set on a new transfer created from the web form
  (`default_get` and onchange on the operation type), not only on `create` without the field.
