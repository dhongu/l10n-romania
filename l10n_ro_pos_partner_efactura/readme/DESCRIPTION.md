When a customer is created or edited from the Point of Sale, the partner form
requires the data an e-Factura (CIUS-RO) invoice needs before it can be sent
to SPV:

- street, city, state (county) and country;
- for Bucharest, the city must be the sector (`Sector 1` ... `Sector 6`).

A company is recognised by its Tax ID (CUI): on 20.0 the partner type is no
longer chosen in the form, so a partner with a valid CUI is a company and one
without a CUI is an individual, invoiced without a Tax ID.

The data is filled in from ANAF when a partner create-by-VAT module is
installed. When ANAF does not answer, the fields stay editable and the cashier
fills them in manually; the partner cannot be saved until they are complete.

The rules apply only to the form opened from POS; partners created from the
back office are not affected. Contact persons of a company are not checked,
their address comes from the company.
