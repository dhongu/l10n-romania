A company buying at the till is identified by its CUI, and e-Factura (SPV) refuses an invoice
whose customer data is incomplete. This module covers both at the Point of Sale.

**The data e-Factura needs.** When a customer is created or edited from the Point of Sale, the
partner form requires the data an e-Factura (CIUS-RO) invoice needs before it can be sent to SPV:

- street, city, state (county) and country;
- the Tax ID (CUI) for companies;
- for Bucharest, the city must be the sector (`Sector 1` ... `Sector 6`).

When ANAF does not answer, the fields stay editable and the cashier fills them in manually; the
partner cannot be saved until they are complete. The rules apply only to the form opened from POS;
partners created from the back office are not affected. Contact persons of a company are not
checked, their address comes from the company.

**The customer by CUI.** Typing a CUI (with or without `RO`) in the *Choose customer* search that
finds nobody in the Point of Sale shows **Search ANAF**:

- a customer already on file under that CUI is offered, even when it is not loaded at the till;
- otherwise the company is fetched from ANAF and created;
- the partner form then opens with the data from ANAF and a warning listing what looks wrong:
  missing data, a street without a number, a city outside its county. The customer goes on the
  order only after **Save**; closing the form leaves it off the order and still to confirm, so
  picking it later from the list opens the form again;
- a company struck off at ANAF is refused; ANAF not answering is told apart from a company that
  does not exist.

With *Romania - Partner Autocomplete from ANAF* installed, the same ANAF data is also offered while
typing the CUI in the *Tax ID* of the customer form, as in the back office.

**The receipt stays a receipt.** Choosing a company as the customer does not tick the invoice: in
Romania the fiscal receipt settles the sale on its own, and the invoice is issued only when the
customer asks for it.
