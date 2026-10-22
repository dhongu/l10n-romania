Looks a Romanian company up at ANAF by its CUI and returns the data for the partner, so that
other modules can create or check a customer without depending on other localization modules.

- **CUI as typed**: with or without `RO`, with spaces or dashes; the control digit is checked
  before ANAF is asked, so a mistyped code does not cost a request.
- **Partner data ready to save**: name, Tax ID (with `RO` only for a VAT payer), street with its
  number, address details, locality without the `Mun.`/`Oraș`/`Com.` prefix, county, postal code,
  trade register number and phone. The fiscal domicile is used, the registered office when it is
  missing.
- **Bucharest**: the locality is the sector (`Sector 3`), as e-Factura requires; when ANAF does
  not write it, it is read from the postal code (`030167` is in Sector 3).
- **Correct diacritics**: ANAF answers with the old cedilla letters (`ş`, `ţ`); they are turned into
  the comma ones (`ș`, `ț`).
- **Status**: VAT payer, inactive and struck off, for the caller to warn about.
- **A clear answer**: found, not found, invalid CUI, or ANAF unavailable — the caller can tell a
  company that does not exist from a service that is down. The wait is short, since somebody is
  usually waiting for the answer.

The module has no screen of its own; it is used by
[l10n_ro_pos_partner_efactura](../l10n_ro_pos_partner_efactura) to bring a company customer in at
the till.

Optional system parameters: `l10n_ro_anaf_partner_lookup.url` (the ANAF service) and
`l10n_ro_anaf_partner_lookup.timeout` (seconds, 10 by default).
