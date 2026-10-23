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
