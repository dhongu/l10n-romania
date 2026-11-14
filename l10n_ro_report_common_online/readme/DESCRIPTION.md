The common building blocks of the Romanian printed reports, for **Odoo Online** too: the
module has no Python code and is imported as a zip (Apps > Import Module). It is the
data-only variant of `l10n_ro_report_common`, for databases where custom Python cannot run.

- **`l10n_ro_report_common_online.banks`**: prints up to 3 of the partner's bank accounts
  ticked *Romania - Print in Report*, in the currency of the document (or of the company).
- **`l10n_ro_report_common_online.report_address_company`**: the company identification
  block: name, address, bank accounts, Tax ID, NRC and share capital.
- **`l10n_ro_report_common_online.amount_in_words`**: the amount in words the way a Romanian
  receipt reads it, written in QWeb. Call it with `amount` and `currency`:

| amount | text |
| --- | --- |
| `500` | *cinci sute de lei* |
| `12000` | *douăsprezece mii de lei* |
| `21000` | *douăzeci și una de mii de lei* |
| `1.01` | *un leu și un ban* |
| `-500.25` | *minus cinci sute de lei și douăzeci și cinci de bani* |

RON is spelled out in Romanian whatever the print language; any other currency keeps the
standard Odoo wording.

The module adds two fields, both manual (`x_`), as Odoo Online requires:

- *Romania - Print in Report* (`x_l10n_ro_print_report`) on bank accounts;
- *Share Capital* (`x_l10n_ro_share_capital`) on the company.

### Odoo Online

The module contains no Python: it can be imported on Odoo Online (Custom plan) from
Apps > Import Module. Do not install it next to `l10n_ro_report_common`: the two modules
keep the same data in different fields.
