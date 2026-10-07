## 20.0.1.0.0 (2026-10-07)

- Migration to 20.0, directly under the new name `l10n_ro_storno_enhancement` (the former
  `l10n_ro_account_storno` never existed on 20.0).
- The migration hooks are kept: databases that reach 20.0 with `l10n_ro_account_storno`
  still installed are taken over when this module is installed. The migration marker
  uses `ir.config_parameter.set_bool` / `get_bool` (`set_param` / `get_param` are removed
  in 20.0).

## 19.0.1.0.0 (2026-10-07)

- Module renamed from `l10n_ro_account_storno` to `l10n_ro_storno_enhancement`: the
  former technical name is already registered on Odoo Apps by another publisher.
- Databases with the former module installed are migrated automatically when the new
  module is installed: fields, views and the account usage values are kept, and the
  former module is removed from the module list (same steps as `merge_module` from
  Odoo upgrade-util, without depending on it).

## 19.0.0.0.5 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.
