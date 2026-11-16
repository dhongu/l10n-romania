## 19.0.1.0.0

- Reduced to the default notice flag on operation types: the rest of the notice
  logic is now in `l10n_ro_stock_account_base`.

- Fix: the default notice flag is also set on a new transfer created from the web form
  (`default_get` and onchange on the operation type), not only on `create` without the field.
