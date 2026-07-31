Common QWeb building blocks shared by the Romanian printed reports
(invoice, sale order, stock picking, balance confirmation):

- **`l10n_ro_report_common.banks`** — prints up to 3 of the partner's bank
  accounts flagged *Print in Report*, in the document currency (falling back
  to the company currency).
- **`l10n_ro_report_common.report_address_company`** — company identification
  block: name, address, bank accounts, Tax ID, NRC and share capital.

Pe lângă șabloane, modulul rescrie **`res.currency.amount_to_text`** pentru
moneda **RON**, astfel încât suma în litere să respecte uzanța contabilă
românească:

| sumă | rezultat |
| --- | --- |
| `500` | *cinci sute lei* |
| `8382.25` | *opt mii trei sute optzeci și doi lei și douăzeci și cinci bani* |
| `1.00` / `1.01` | *un leu* / *un leu și un ban* |
| `-500` | *minus cinci sute lei* |

Odoo standard construiește textul din denumirile unității monetare și îl scrie
cu inițiale majuscule, rezultând *„Cinci Sute Leu"* — inutilizabil pe o
chitanță. Particula gramaticală *de* (*douăzeci **de** lei*) este omisă
**intenționat**, pentru a păstra formularea folosită de programele de
contabilitate românești. Formularea nu depinde de limba de tipărire: o sumă în
lei pe un document legal românesc se citește în română și pe o factură în
engleză. Pentru orice altă monedă se păstrează comportamentul standard Odoo.

### Cerințe tehnice

- Necesită biblioteca `num2words` (`pip3 install num2words>=0.5.12`). Dacă
  lipsește, se folosește formularea implicită Odoo.

The module also adds the two supporting fields:

- *Print in Report* (`l10n_ro_print_report`) on bank accounts;
- *Share Capital* (`l10n_ro_share_capital`) on the company.

The field names match the ones historically provided by the OCA
`l10n_ro_config` module, so databases migrating away from the OCA stack keep
their configuration without any data migration. Both modules can be installed
side by side.
