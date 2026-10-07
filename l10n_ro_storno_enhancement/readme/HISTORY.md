## 18.0.1.0.0 (2026-10-07)

- Module renamed from `l10n_ro_account_storno` to `l10n_ro_storno_enhancement`: the
  former technical name is already registered on Odoo Apps by another publisher.
- Databases with the former module installed are migrated automatically when the new
  module is installed: fields, views and the account usage values are kept, and the
  former module is removed from the module list (same steps as `merge_module` from
  Odoo upgrade-util, without depending on it).
