**No longer developed.** For a Romanian company, use `l10n_ro_partner_autocomplete`: it fills
the partner in from ANAF, for free and without an OpenAPI key, and does not depend on the OCA
`l10n_ro_partner_create_by_vat`, which this module needs. This module only receives fixes until
the databases that use it have switched.

This modules adds the "Get Partner Data OpenAPI" in the contact from, by
adding the vat number in the name field and pressing the button the
modules starts a search using your OpenAPI key and fills in the
information in the empty fields.
