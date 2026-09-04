To import a bank statement exported from Revolut Business:

1. Go to *Accounting > Accounting > Bank*, open the Revolut journal (bank BIC starting with `REVO`).
2. Click *Import* and select the MT940 file exported from the Revolut Business dashboard.
3. A single Revolut export can contain one block per currency wallet, all reported under the same IBAN. Each currency block is imported into its own bank journal for that currency; several journals can be linked to the same IBAN (one per currency wallet), and each wallet is matched to the journal of the same currency. A wallet is silently skipped (instead of blocking the whole import) if there is no journal on the same IBAN configured for its currency, so make sure you have created a journal per currency wallet you want to import before uploading the file.
4. Odoo creates a bank statement per matching journal, with partner name, counterparty IBAN and payment reference filled in from the file.
