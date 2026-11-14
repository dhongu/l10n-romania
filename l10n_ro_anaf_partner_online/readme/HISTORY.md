## 19.0.1.0.1 (2026-11-14)

- Cannot be installed together with `l10n_ro_partner_create_by_vat` or `l10n_ro_partner_autocomplete`,
  the modules with Python code that fill the partner from ANAF too: the manifest lists them under
  `excludes`.

# 19.0.1.0.0

- First version: ANAF button on the partner form (immediate answer), *Update from ANAF* on a
  selection of partners (queued answer), activation by callback, ANAF status on the partner.
- Consultant sheet (`readme/FISA_CONSULTANT.md`), `readme/USAGE.md` and screenshots (RO, EN).
