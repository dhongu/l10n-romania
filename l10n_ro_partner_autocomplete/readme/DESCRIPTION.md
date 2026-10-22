The standard partner autocomplete of Odoo suggests companies from IAP and spends credits to
fill the partner in. For a Romanian company the authoritative source is ANAF, and it is free.

With this module, typing a Romanian CUI where Odoo offers the autocomplete — the *Tax ID* or the
*Name* of a partner, the *Customer* of a quotation or an invoice, the customer form opened from the
Point of Sale — shows the company found at ANAF. Choosing it fills the partner in:

- name, Tax ID (with `RO` only for a VAT payer), street with its number, address details,
  locality, county, postal code, trade register number and phone;
- for Bucharest, the sector as the locality, as e-Factura requires;
- a note in the chatter that the data was taken from ANAF, with the date.

No IAP credit is used for a Romanian CUI: neither the search nor the enrichment goes to IAP.

The CUI is recognised with or without `RO`. The rest is left to IAP as before: a search by company
name, a company from another country, and a Romanian CUI when ANAF does not answer.
