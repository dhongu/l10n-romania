The standard partner autocomplete of Odoo suggests companies from IAP and spends credits to
fill the partner in. For a Romanian company the authoritative source is ANAF, and it is free.

With this module, typing a Romanian CUI where Odoo offers the autocomplete — the *Tax ID* or the
*Name* of a partner, the *Customer* of a quotation or an invoice, the customer form opened from the
Point of Sale — shows the company found at ANAF. Choosing it fills the partner in:

- name, Tax ID (with `RO` only for a VAT payer), street with its number, address details,
  locality, county, postal code, trade register number and phone;
- for Bucharest, the sector as the locality, as e-Factura requires;
- a note in the chatter that the data was taken from ANAF, with the date.

**Update from ANAF.** On a Romanian company with a Tax ID, the **Update from ANAF** button below
the Tax ID reloads the data from ANAF: name, address, Tax ID and trade register number are
rewritten, a phone already on the partner is kept. The chatter lists every field changed, with
its old and new value, and says when ANAF lists the company as struck off or inactive.

**A partner created with its CUI as the name.** Typing a CUI in a field such as *Customer* and
choosing *Create*, or importing partners whose name is a CUI, fills them in from ANAF too. Values
given explicitly are kept; a partner that already has a Tax ID, a contact person or a partner
from another country is left as it is. The `l10n_ro_anaf_no_autofill` context key turns it off,
for instance for a bulk import.

**City and postal code.** With the list of Romanian cities (`l10n_ro_city`), the city is chosen
from it as well. Choosing a city then keeps the postal code the partner already has, instead of
replacing it with the city's.

No IAP credit is used for a Romanian CUI: neither the search nor the enrichment goes to IAP.

The CUI is recognised with or without `RO`. The rest is left to IAP as before: a search by company
name, a company from another country, and a Romanian CUI when ANAF does not answer.

The **Enrich** action of the partner list and form (Odoo 20) asks ANAF as well for a Romanian
company, by its Tax ID or its Company ID, and fills only the fields the partner does not have yet.
