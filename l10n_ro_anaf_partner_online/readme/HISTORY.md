# 20.0.1.0.2 (2026-11-14)

- Apps Store banner: the "IAP" label shows that the module works with IAP credits.

# 20.0.1.0.1 (2026-11-14)

- Cannot be installed together with `l10n_ro_partner_create_by_vat` or `l10n_ro_partner_autocomplete`,
  the modules with Python code that fill the partner from ANAF too: the manifest lists them under
  `excludes`.
- The zip import (*Apps > Import Module*) does not check `excludes`: a guard on the first field
  stops it while `l10n_ro_partner_create_by_vat` or `l10n_ro_partner_autocomplete` is installed.

# 20.0.1.0.0

- Migration to 20.0: access rights in `security/ir.access.csv`; the ANAF button sits after the Tax
  ID in the row `vat_div` of the standard form (already a row on 20.0, no field move); Owl 3
  widget (`useProps`, `proxy`, notification plugin, `oi` icons); `is_company` is no longer written
  (computed on 20.0 from the Tax ID).

# 19.0.1.0.0

- First version: ANAF button on the partner form (immediate answer), *Update from ANAF* on a
  selection of partners (queued answer), activation by callback, ANAF status on the partner.
- Consultant sheet (`readme/FISA_CONSULTANT.md`), `readme/USAGE.md` and screenshots (RO, EN).
