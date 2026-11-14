**Before**: the company has a Tax ID and is connected to the SPV in *Invoicing (Accounting) >
Configuration > Settings*, block **Romanian E-Factura** (Client ID, Client Secret, **Generate
Token**), as for the standard module.

1. Go to *Invoicing > SPV Messages* (*Accounting > SPV Messages*). The messages are grouped by
   status: **Error**, **Sent** (waiting for ANAF), **Validated**. **Received** is ticked on the
   vendor bills downloaded from the SPV.

   ![The SPV Messages register grouped by status: one invoice in Error with the BR-RO-110 message, one Sent and four Validated, two of them vendor bills ticked in the Received column; the Synchronize now button and the SPV Messages menu are highlighted](static/description/en/01_lista_mesaje.png)

2. Open the filters: **Sent** / **Received** show only the invoices sent or only the bills
   received, **Refused** the invoices refused by ANAF and **Errors** the messages with an error
   text. Group by **Status**, **Direction**, **Partner** or **Date**.

   ![The filter menu open over the register: Sent, Received, Refused and Errors highlighted; on the right, Group By Status (ticked), Direction, Partner and Date](static/description/en/02_filtre.png)

3. Open a received bill: the invoice is linked at the top; **XML of the message** downloads the
   signature of ANAF and **Invoice files** holds the XML and the PDF of the vendor bill.

   ![The SPV message of the vendor bill BILL/2026/11/0002 from Gama Logistic SRL, validated: Received ticked, the download key 5012345674 and, under Files, the signature XML plus the PDF and the XML of the bill, highlighted](static/description/en/03_mesaj_primit.png)

4. Open a refused invoice: **Message** gives the reason of ANAF. Correct the invoice and send it
   again from the invoice, as in the standard module. On an invoice still waiting for ANAF, **Fetch
   status** asks ANAF for that invoice only.

   ![The SPV message of the invoice INV/2026/00012 in Error: the Message block, highlighted, with E: BR-RO-110 and the reason given by ANAF](static/description/en/04_mesaj_respins.png)

5. Click **Synchronize now** to fetch the latest messages from ANAF: a window asks first for the
   date to synchronize from (up to 60 days back), then the status of the invoices sent and the new
   vendor bills, created as drafts, are brought in. On a company
   without a Tax ID or not connected to the SPV, the button says what to set first. The button is
   for the users with invoicing rights.

   ![The Invalid Operation window after Synchronize now on a company not connected: The company RO Company is not connected to the SPV yet, with the path Invoicing (Accounting) > Configuration > Settings, Romanian E-Factura, Generate Token](static/description/en/05_sincronizare.png)
