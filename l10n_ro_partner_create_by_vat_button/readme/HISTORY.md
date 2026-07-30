## 19.0.1.1.8 (2026-07-30)

- Remove the dead `_fix_vat_number` override. That hook was removed from
  `base_vat` in 19.0 - normalisation moved to `_run_vat_checks` and
  `_format_vat_number`, which take a country code instead of a country id - so
  the override was never called and its `super()` call would have raised
  `AttributeError`. Nothing replaces it: unlike the 18.0 helper,
  `_format_vat_number` only formats the number and never prepends the country
  prefix, so the `skip_ro_vat_change` guard has nothing left to suppress.
- The prefix that was in fact being forced onto foreign tax IDs came from
  `l10n_ro_config._split_vat`, which deduced the country code from a database
  lookup; it is fixed there (OCA/l10n-romania#1551).
