## 20.0.1.2.1 (2026-10-29)

- The tax code is normalised on save as while typing: spaces, dots and dashes between the digits
  no longer reject an address whose company was found at ANAF. Consultant sheet with screenshots.

## 20.0.1.2.0 (2026-10-28)

- Migration to Odoo 20.0. The *Company* field of the address form is `parent_name`: the look-up
  fills it in, and the ANAF legal name goes to the company (the commercial entity of the invoice)
  instead of renaming the contact. No `is_company` is written: Odoo computes it from the Tax ID,
  and deduces the CUI (`RO_EN` identifier) from it. The look-up answer has the trade register
  number under `nrc`; `company_registry` is kept for the forms that still map it.

## 19.0.1.2.0 (2026-10-23)

- The ANAF look-up goes through `l10n_ro_anaf_partner_lookup` instead of
  `l10n_ro_partner_create_by_vat` (OCA): the module no longer depends on OCA. The locality, the
  Bucharest sector and the postal code follow its rules; the API key parameters of
  `l10n_ro_partner_create_by_vat` are no longer read (the ANAF v9 service needs none).

## 19.0.1.1.1 (2026-10-22)

- Odoo Apps banner title: *Website ANAF* (was *Website ANAF Prefill*), the same as the module name.

## 19.0.1.1.0 (2026-10-12)

- Renamed from `l10n_ro_website_anaf_prefill` (not installed anywhere yet): the module now also
  checks the tax code when the address is sent, the Romanian part that was in
  `deltatech_website_vat_validation` (CNP message, company not found or struck off refused, legal
  name and empty fields from ANAF, notes on the cart for an inactive company or ANAF unavailable).
  While an older `deltatech_website_vat_validation` still makes that check, this one stands aside.

## 19.0.1.0.0 (2026-10-11)

- First version: ANAF look-up while the tax code is typed in the address form of the website.
