No configuration. The ANAF address and the API key, if any, are those of
`l10n_ro_partner_create_by_vat` (system parameters `l10n_ro_partner_create_by_vat.*`).

The module only fills in the form. The checks when the address is submitted (tax code refused
when not found or struck off) are done by `deltatech_website_vat_validation`, when installed.
