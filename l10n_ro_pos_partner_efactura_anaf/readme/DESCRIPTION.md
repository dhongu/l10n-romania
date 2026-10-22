The ANAF data of a company is often incomplete or outdated: a street without a
number, a city that is not in the declared county, details of the address moved
into the street. e-Factura (SPV) refuses an invoice with such an address, and
by then the customer has left the shop.

This module joins *Romania - POS Partner e-Factura Check* and *Romania - Point
of Sale Partner* (OCA), and is installed automatically when both are present.
A customer fetched with **Create from ANAF** in the Point of Sale is no longer
put on the order directly:

- the partner form opens with the data from ANAF and a warning listing what
  looks wrong: missing data, a street without a number, a city that is not in
  the county;
- the cashier checks the data against the customer's documents, corrects it
  and saves; the form cannot be saved while the data e-Factura needs is
  missing;
- only then the customer is put on the order. Closing the form without saving
  leaves the customer off the order, still waiting to be confirmed: picking it
  later from the customer list opens the form again.

A customer already on file, found by its Tax ID, goes on the order directly,
unless its data is incomplete; then it is confirmed the same way.
