Common QWeb building blocks shared by the Romanian printed reports
(invoice, sale order, stock picking, balance confirmation):

- **`l10n_ro_report_common.banks`** — prints up to 3 of the partner's bank
  accounts flagged *Print in Report*, in the document currency (falling back
  to the company currency).
- **`l10n_ro_report_common.report_address_company`** — company identification
  block: name, address, bank accounts, Tax ID, NRC and share capital.

The module also adds the two supporting fields:

- *Print in Report* (`l10n_ro_print_report`) on bank accounts;
- *Share Capital* (`l10n_ro_share_capital`) on the company.

The field names match the ones historically provided by the OCA
`l10n_ro_config` module, so databases migrating away from the OCA stack keep
their configuration without any data migration. Both modules can be installed
side by side.
