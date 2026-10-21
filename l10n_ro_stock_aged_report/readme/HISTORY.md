## 19.0.1.0.2 (2026-10-21)

- Without a product selected, the report now covers the whole stock of the chosen locations.
  It used to read only the first 10,000 products, so on larger catalogues the remaining
  products were left out silently and the total no longer matched the stock.
- The report lines are created in a single batch instead of one by one, which keeps the
  report fast on warehouses with tens of thousands of quants.

## 19.0.1.0.1 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.1.0.0 (2026-10-07)

- Module renamed from `l10n_ro_stock_age_report` to `l10n_ro_stock_aged_report`: the
  former technical name is already registered on Odoo Apps by another publisher.
- Databases with the former module installed are migrated automatically when the new
  module is installed: fields, views, actions, menus and the last in/out dates on the
  quants are kept, and the former module is removed from the module list (same steps as
  `merge_module` from Odoo upgrade-util, without depending on it).

## 19.0.0.0.4 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.
