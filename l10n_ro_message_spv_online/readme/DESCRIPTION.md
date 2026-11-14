A register of the e-Factura (SPV) messages for **Odoo Online** too: the module has no Python code
and is imported as a zip (Apps > Import Module). It works on top of the standard Romanian
e-Factura module (`l10n_ro_edi`), which sends the invoices and downloads the vendor bills; this
module only shows what the standard module already keeps, in one place.

- **SPV Messages menu** in Accounting (Invoicing): the last SPV message of each invoice sent and
  each bill received, grouped by status (*Sent*, *Validated*, *Error*).
- **Filters**: sent / received, waiting for ANAF, validated, refused, with an error message, by
  date; group by status, direction, partner or month.
- **Message form**: the invoice, the partner, the total, the message of ANAF, the download key,
  the XML of the message (the invoice sent, or the signature of ANAF) and the files of the invoice
  (the XML and the PDF of a received bill), all downloadable. The list shows the partner and the
  date of the invoice; the total is on the form.
- **Synchronize now**: runs the standard synchronization with the SPV (status of the invoices
  sent, new vendor bills) without waiting for the scheduled action; on a company without a Tax ID
  or without an SPV token, it says what to set first.

What it does not do: it does not match the products by the vendor code or create the partners
from the CUI; on a server with Python, the OCA module `l10n_ro_message_spv` does that. The ANAF
token stays in your database; apart from the standard synchronization with the SPV of ANAF,
the module sends no data anywhere.
