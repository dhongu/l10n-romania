The Romanian layout of the invoice and of the cash receipt (*chitanță*), for **Odoo Online**
too: the module has no Python code and is imported as a zip (Apps > Import Module). It is the
data-only variant of `l10n_ro_invoice_report`, for databases where custom Python cannot run.
It needs `l10n_ro_report_common_online`, imported first.

**Invoice** (the standard *Invoices* report, changed in place):

- header with the supplier and the customer side by side: address, bank accounts, CIF, NRC,
  share capital, VAT on payment, delivery address; the operating unit of the journal, when set;
- lines: optional line number, unit price without VAT, VAT value per line, optional total with
  VAT, optional list price before discount, the product name removed from the description on
  request; credit notes printed with negative values;
- footer: issuer, delegate and means of transport, the deliveries (or receptions) of the
  invoice with their AWB numbers, the legal mention that the invoice is valid without signature
  and stamp, the additional info of the customer, the optional Coface logo;
- invoices paid in cash carry the cash receipt below, with the amount in words.

**Other reports**: *Voucher / Payment* (receipt or payment disposal, Form 14-4-1 / 14-4-4 for
the cash desk) and *Invoices in company language*.

**Settings** are on the company, *Romanian Invoice* tab: e-mail, phone and marker in the
addresses, line number, total with VAT, list price before discount, product name, payment
communication, deliveries, delegate, Coface logo.

**Automations** (instead of Python): the delegate brings its means of transport on the invoice;
the partner's *Payment bank account* is set on its customer invoices; the action *Set origin from
pickings* writes the deliveries in the origin of the invoice.

What it does not do, compared with `l10n_ro_invoice_report`: no changes to the bank statements
and no default delegate from the context.

### Odoo Online

The module contains no Python: it can be imported on Odoo Online (Custom plan) from
Apps > Import Module. It cannot be installed next to `l10n_ro_invoice_report` (the manifest
excludes it): the two modules keep the same data in different fields.
