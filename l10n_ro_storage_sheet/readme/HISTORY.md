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

