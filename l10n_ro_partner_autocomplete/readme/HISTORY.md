## 20.0.1.3.0 (2026-10-28)

- Migration to 20.0. `is_company` is computed from the Tax ID and the CUI is the Company ID
  (`RO_EN`) deduced from it: the ANAF data no longer carries either.
- The **Update from ANAF** link sits below the Tax ID row, next to which 20.0 shows the identifiers.
- The **Enrich** action (new in 20.0) answers a Romanian CUI from ANAF, without IAP credit.

## 19.0.1.3.0 (2026-10-27)

- It cannot be installed together with the OCA `l10n_ro_partner_create_by_vat` (`excludes`): both
  fill the partner from ANAF, each its own way. Uninstall it first, with the modules that depend on
  it (`l10n_ro_partner_create_by_vat_button`, `l10n_ro_fiscal_validation`).

## 19.0.1.2.0 (2026-10-23)

- The ANAF suggestion carries the `city_id` found by `l10n_ro_anaf_partner_lookup`.
- For a Romanian partner, choosing the city keeps the postal code already there (base_address_extended
  would replace it with the city's, often empty for a town), and a city set together with its postal
  code is not replaced from that postal code (`l10n_ro_city` picks the Bucharest sector from it, and
  ANAF sometimes gives a postal code of another sector).

## 19.0.1.1.3 (2026-10-23)

- Main image for the Odoo Apps Store (banner); the manifest points to it in `images`.

## 19.0.1.1.2 (2026-10-23)

- A note under *Partner Autocomplete* in the settings says that Romanian companies are filled in
  from ANAF without IAP credits, and what the credits are still used for.

## 19.0.1.1.1 (2026-10-23)

- A partner created with a CUI as its name is filled in from ANAF also when its Tax ID is that
  same CUI, as `l10n_ro_partner_create_by_vat_button` sets it before this module runs; a Tax ID
  of another company still leaves the partner as it is.

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
