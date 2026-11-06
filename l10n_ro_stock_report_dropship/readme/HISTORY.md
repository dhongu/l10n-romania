## 19.0.1.1.3 (2026-11-06)

- Readme: the module extends the OCA `l10n_ro_stock_report` on the OCA valuation engine
  `l10n_ro_stock_account`, not `l10n_ro_storage_sheet` (the storage sheet on the native
  valuation), which has no dropship extension.

## 19.0.1.1.2 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.1.1.1 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.

## 19.0.1.1.0 (2026-08-18)

**Bugfix**

- The dropship rows of the storage sheet are again reported under the account
  the movement is valued on (usually 371000), instead of being grouped under a
  separate "no account" bucket. The dropship insert left `account_id` NULL, so
  the dropship never appeared under the goods account the accountant
  reconciles - the sheet looked as if the dropship line was missing, even
  though its in/out values were correct. Up to 18.0 the account came from the
  valuation layer, and it was dropped when the module was ported to 19.0.
