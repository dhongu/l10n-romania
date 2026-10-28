## 19.0.1.1.12 (2026-10-23)

- VIES lookup over HTTPS. The European Commission now answers 403 Forbidden on the
  `http://` address of the VIES WSDL, so *Get partner data* from VIES failed with a server
  error. When the service cannot be reached, the user now gets a message instead of a
  traceback.

## 19.0.1.1.11 (2026-10-22)

- Odoo Apps banner title: *Partner Create by VAT Button* (was *Partner Data Refresh by VAT*), the same as the module name.

## 19.0.1.1.10 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.1.1.9 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.

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
