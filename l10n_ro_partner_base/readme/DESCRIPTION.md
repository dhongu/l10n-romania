Romanian VAT/CUI handling on partners and partner data from ANAF and VIES.
It is the Terrabit replacement of the OCA `l10n_ro_config`,
`l10n_ro_partner_create_by_vat`, `l10n_ro_partner_create_by_vat_button` and
`l10n_ro_partner_unique` modules, written from scratch for what the Terrabit modules use.

- **Fields**: `l10n_ro_vat_subjected` and `l10n_ro_vat_number` on partners,
  `l10n_ro_caen_code` on companies (the CAEN code is no longer kept on
  partners).
- **CUI logic**: the CUI can be written without the `RO` prefix; the prefix is
  added for VAT payers and removed for the others.
- **ANAF**: the "Get Data" button on the partner form reads the company data
  from the ANAF VAT payer web service (v9). A partner created with a CUI as its
  name (`RO14431470` or `14431470`) is completed from ANAF at creation; a name
  like `DE123456789` is completed from VIES.
- **VIES**: for non-Romanian partners (needs the `zeep` python package).

The web service URL can be changed with the system parameter
`l10n_ro_partner_base.anaf_url`.

**Unique partners.** Two company partners (without parent) of a company whose
fiscal country is Romania cannot have the same VAT, with or without the `RO`
prefix. The check is chosen in *Settings > Contacts > Unique Partners
(Romania)*, which stores the system parameter
`l10n_ro_partner_unique.vat_nrc_unique` (the same one as the OCA module):

- `off` (default): not checked;
- `vat`: unique VAT;
- `vat_nrc`: unique VAT and NRC (a partner without NRC counts as a match).

When the module is installed on a database that has the OCA
`l10n_ro_partner_unique` installed, the parameter is set to `vat` if it was not
set, so the check keeps working. Do not set `off` while the OCA module is still
installed: it has no "off" value and would block every company partner.
