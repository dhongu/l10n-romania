Default sale and purchase taxes for **service** products on Romanian companies.

The Romanian chart of accounts ships separate VAT taxes for services
(*TVA colectat 21% Servicii*, *TVA deductibil 21% Servicii*, `21% S`) next to
the ones for goods (`21% G`). On domestic invoices both report on the same
D300 rows, but the EU fiscal positions map them by type: a service sold to or
bought from an EU partner must carry `21% S` to land on the intra-community
services rows (D300 row 3, rows 7/22) instead of the goods rows (row 1,
rows 5/20), and with the services codes (P, S) instead of the goods codes
(L, A) in the recapitulative statement D390. Odoo has a single pair of
default taxes per company, so a new service product would otherwise get the
goods taxes.

The module adds:

- *Default Service Taxes* in **Accounting > Settings > Taxes**, next to the
  standard default taxes (visible for companies with Romania as fiscal country);
- the values `tvac_21_s` / `tvad_21_s` filled in when the Romanian chart of
  accounts is loaded, and at install time for companies that already have it;
- on the product form, when the type becomes *Service*, the service taxes
  replace the product taxes (including taxes set by hand); when the type changes back, the service taxes
  are replaced by the company default taxes (taxes set by hand are kept).

The field names match the ones historically provided by the OCA
`l10n_ro_config` module, so databases migrating away from the OCA stack keep
their configuration without any data migration. Both modules can be installed
side by side.
