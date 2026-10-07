## 19.0.1.0.0 (2026-10-07)

- Module renamed from `l10n_ro_stock_age_report` to `l10n_ro_stock_aged_report`: the
  former technical name is already registered on Odoo Apps by another publisher.
- Databases with the former module installed are migrated automatically when the new
  module is installed: fields, views, actions, menus and the last in/out dates on the
  quants are kept, and the former module is removed from the module list (same steps as
  `merge_module` from Odoo upgrade-util, without depending on it).

## 19.0.0.0.4 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.
