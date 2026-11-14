**Before**: the company is connected to the SPV in *Accounting > Configuration > Settings*, block
**Romanian E-Factura** (Client ID, Client Secret, **Generate Token**), as for the standard module.

1. Go to *Accounting > SPV Messages* (*Invoicing > SPV Messages*). The messages are grouped by
   status: **Sent** (waiting for ANAF), **Validated**, **Error**.
2. Click **Synchronize now** to fetch the latest messages from ANAF: the status of the invoices
   sent and the new vendor bills, created as drafts. On Odoo 20, a window first asks for the
   period.
3. Use the filters **Sent** / **Received** to see only the invoices sent or only the bills
   received, **Refused** or **Errors** for those that need a correction, and the grouping by
   **Partner** or **Date**.
4. Open a message: the invoice is linked at the top; **XML of the message** downloads the invoice
   sent or the signature of ANAF, **Invoice files** holds the XML and the PDF of a received bill.
   On an invoice still waiting for ANAF, **Fetch status** asks ANAF for that invoice only.
