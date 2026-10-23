## 19.0.1.1.0 (2026-10-23)

- **Update from ANAF** button on a Romanian company: the data is reloaded from ANAF, a phone
  already set is kept, and the chatter lists the changed fields with their old and new value.
- A partner created with a Romanian CUI as its name (quick create, import, API) is filled in
  from ANAF; the `l10n_ro_anaf_no_autofill` context key turns it off.

## 19.0.1.0.1 (2026-10-22)

- Depends on `l10n_ro_anaf_partner_lookup`, the new name of `l10n_ro_anaf_lookup`.

## 19.0.1.0.0 (2026-10-22)

- Initial version: the partner autocomplete answers a Romanian CUI (with or without `RO`) from
  ANAF instead of IAP, search and enrichment, without IAP credits; IAP keeps the name search,
  the other countries and the case when ANAF does not answer.
