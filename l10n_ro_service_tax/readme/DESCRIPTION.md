Default sale and purchase taxes for **service** products on Romanian companies.

The Romanian chart of accounts ships separate VAT taxes for services
(*TVA colectat 21% Servicii*, *TVA deductibil 21% Servicii*), reported on
other D300 rows than the taxes for goods. Odoo has a single pair of default
taxes per company, so a new service product would otherwise get the goods
taxes and land on the wrong declaration row.

The module adds:

- *Default Service Taxes* in **Accounting > Settings > Taxes**, next to the
  standard default taxes (visible for companies with Romania as fiscal country);
- the values `tvac_21_s` / `tvad_21_s` filled in when the Romanian chart of
  accounts is loaded, and at install time for companies that already have it;
- on the product form, when the type becomes *Service*, the service taxes
  replace the product taxes; when the type changes back, the service taxes
  are replaced by the company default taxes (taxes set by hand are kept).

The field names match the ones historically provided by the OCA
`l10n_ro_config` module, so databases migrating away from the OCA stack keep
their configuration without any data migration. Both modules can be installed
side by side.
