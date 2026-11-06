## 19.0.1.0.2 (2026-11-06)

- **The printed storage sheet (Show Sheet Pdf) came out without any move.** Both PDF templates
  group the lines by account, but on 19.0 the report never filled the account in: up to 18.0 it
  came from the valuation layer, which no longer exists. The lines now get the stock valuation
  account of the product (category account, then the company default), and lines that still have
  no account are printed without the account header instead of being left out. In the pivot the
  *Account* grouping now shows the stock account instead of an empty row. The per-product
  template uses `t-out` instead of the deprecated `t-raw`. `stock_account` is now declared in
  `depends` (the report reads the move values and the valuation account from it; it was installed
  only through auto-install).
- Consultant sheet: new step with the printed sheet. Printed sheet header: *Date* column (was
  hard-coded in Romanian), *Valoare ieșire* in the Romanian translation.

## 19.0.1.0.1 (2026-11-06)

- No longer depends on the OCA module `l10n_ro_config`. It was used only to set
  `is_l10n_ro_record` on the *Romanian Stock Sheet Report* menu, a field with no effect on
  menus. No functional change.
- Consultant sheet with screenshots; Romanian translation fixes (*Cantitate ieșită*, *Preț unitar ieșire*,
  *Factură fiscală*).

## 19.0.1.0.0 (2026-10-14)

- Renamed from `l10n_ro_stock_report` to `l10n_ro_storage_sheet`, together
  with its models (`l10n.ro.stock.storage.sheet` -> `l10n.ro.storage.sheet`,
  `l10n.ro.stock.storage.sheet.line` -> `l10n.ro.storage.sheet.line`). The old
  name clashed with the OCA module `l10n_ro_stock_report`, and the copy that
  loaded depended only on the order of the repositories in `addons_path`.
  No migration of the module record: the report models are transient, and the
  old name now belongs to the OCA module. See `INSTALL.md` for databases that
  have the storage sheet without `l10n_ro_stock_account`.

## 19.0.2.0.1 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

