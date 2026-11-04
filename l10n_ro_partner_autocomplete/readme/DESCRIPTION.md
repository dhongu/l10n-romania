The standard partner autocomplete of Odoo suggests companies from IAP and spends credits to
fill the partner in. For a Romanian company the authoritative source is ANAF, and it is free.

With this module, typing a Romanian CUI where Odoo offers the autocomplete — the *Tax ID* or the
*Name* of a partner, the *Customer* of a quotation or an invoice, the customer form opened from the
Point of Sale — shows the company found at ANAF. Choosing it fills the partner in:

- name, Tax ID (with `RO` only for a VAT payer), street with its number, address details,
  locality, county, postal code, trade register number and phone;
- for Bucharest, the sector as the locality, as e-Factura requires;
- a note in the chatter that the data was taken from ANAF, with the date.

**Companies from other EU countries, from VIES.** A VAT number with the prefix of another EU country
(`IT00743110157`, `HU10773381`) is looked up in VIES, the free service of the European Commission:
the name, street, postal code, city and country are filled in, with a note in the chatter, and no IAP
credit is used. When VIES does not answer, does not know the number or the country keeps the name to
itself (Germany, Spain), IAP is asked as before. The update button next to the Tax ID of such a
company reloads the data from VIES and sets *Intra-Community Valid*.

**VIES for a Romanian company.** For a VAT payer, the note after the ANAF data says whether the company
is in VIES, that is registered for intra-community operations; a VAT payer is not always.

**Update from ANAF.** On a Romanian company with a Tax ID, the **Update from ANAF** button (the refresh
icon) next to the Tax ID reloads the data from ANAF: name, address, Tax ID and trade register number are
rewritten, a phone already on the partner is kept. The chatter lists every field changed, with
its old and new value, and says when ANAF lists the company as struck off or inactive.

**A partner created with its CUI as the name.** Typing a CUI in a field such as *Customer* and
choosing *Create*, or importing partners whose name is a CUI, fills them in from ANAF too. Values
given explicitly are kept; a partner that already has a Tax ID, a contact person or a partner
from another country is left as it is. The `l10n_ro_anaf_no_autofill` context key turns it off,
for instance for a bulk import.

**VAT payer.** A Romanian company shows **VAT Payer** next to its Tax ID, filled in from ANAF together
with the rest of the data. The partner also keeps its Tax ID without the country prefix. Both
fields have the names used by the other Romanian localization modules, so no other module is
needed for them.

**City and postal code.** With the list of Romanian cities (`l10n_ro_city`), the city is chosen
from it as well. Choosing a city then keeps the postal code the partner already has, instead of
replacing it with the city's.

No IAP credit is used for a Romanian CUI: neither the search nor the enrichment goes to IAP.

The CUI is recognised with or without `RO`. The rest is left to IAP as before: a search by company
name, a company from outside the EU, a company from the EU that VIES does not describe, and a
Romanian CUI when ANAF does not answer.
