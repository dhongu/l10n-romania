The module installs automatically as a dependency of the modules that use it and needs no
setup. It works out of the box with the default ANAF service and a 10-second wait.

Optional system parameters, for administrators only (activate developer mode, then go to
**Settings → Technical → Parameters → System Parameters** and add the keys you need):

- `l10n_ro_anaf_partner_lookup.url`: address of the ANAF service. Change it only if ANAF
  changes it.
- `l10n_ro_anaf_partner_lookup.timeout`: seconds to wait for ANAF (default 10). It applies to the
  back office and to the Point of Sale; the website has its own fixed 5-second wait. The value must
  be a **positive whole number** (for example `15`). A value such as `10.5`, `ten` or `0` makes
  every back-office and POS lookup report "ANAF unavailable" until it is corrected.
- `l10n_ro_anaf_partner_lookup.vies_url`: address of the VIES service (default
  `https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{country}/vat/{number}`). Keep the
  `{country}` and `{number}` placeholders.
- `l10n_ro_anaf_partner_lookup.vies_timeout`: seconds to wait for VIES (default 10, also a
  positive whole number).

Optional modules that complete the result:

- `l10n_ro_zip`: fills the postal code by street and number when ANAF does not provide it.
- `l10n_ro_city`: picks the city from the list of Romanian localities.
- `l10n_ro` (Romanian localization): provides the **NRC** field and computes **Company ID** from
  the Tax ID.
