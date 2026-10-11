## 19.0.1.1.0 (2026-10-12)

- Renamed from `l10n_ro_website_anaf_prefill` (not installed anywhere yet): the module now also
  checks the tax code when the address is sent, the Romanian part that was in
  `deltatech_website_vat_validation` (CNP message, company not found or struck off refused, legal
  name and empty fields from ANAF, notes on the cart for an inactive company or ANAF unavailable).
  While an older `deltatech_website_vat_validation` still makes that check, this one stands aside.

## 19.0.1.0.0 (2026-10-11)

- First version: ANAF look-up while the tax code is typed in the address form of the website.
