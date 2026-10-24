## 19.0.1.2.0 (2026-10-24)

- The whole address comes from one ANAF block: the fiscal domicile, else the registered office.
  The postal code is no longer taken from the other block or from the general data, which gave
  addresses that do not exist (a street in Sector 2 with a postal code from Sector 6).
- When the block has no postal code and `l10n_ro_zip` is installed, it is looked up in `res.zip`
  by street, locality and county, with the number ranges of long streets (odd and even apart); a
  village without streets gets the postal code of the locality. Without a single match it stays
  empty.

## 19.0.1.1.0 (2026-10-23)

- Where the partner has a `city_id` (base_address_extended, with the cities of `l10n_ro_city`),
  it is filled in too: the Bucharest sector, else the locality by name in its county, told apart
  by the commune ANAF writes next to a village and then by the postal code, else by the postal
  code (street by street with `l10n_ro_zip`). Without a single match it is left empty.

## 19.0.1.0.3 (2026-10-23)

- Main image for the Odoo Apps Store (banner); the manifest points to it in `images`.

## 19.0.1.0.2 (2026-10-23)

- The caller can choose how long to wait for ANAF (`timeout`); the result also gives the date the
  company became inactive and the trade register number, even when the partner has no field for
  it.

## 19.0.1.0.1 (2026-10-23)

- A village is the locality without its commune or town: "Sat Filipești Com. Filipești" gives
  "Filipești"; the "Orș." prefix of a town is removed too.
- The trade register number (J…) goes only to the NRC field: the Company ID stays the CUI,
  as `l10n_ro` computes it from the Tax ID and e-Factura uses it.

## 19.0.1.0.0 (2026-10-22)

- Initial version: ANAF lookup by CUI (v9 service) returning the partner data, the VAT payer,
  inactive and struck off status, with the CUI control digit checked first and the Bucharest
  sector as the locality (taken from the postal code when ANAF does not write it).
- Named `l10n_ro_anaf_partner_lookup` (first published as `l10n_ro_anaf_lookup`, renamed
  before any installation); the system parameters are `l10n_ro_anaf_partner_lookup.url` and
  `l10n_ro_anaf_partner_lookup.timeout`.
