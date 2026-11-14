Adds the **supporting document type** (`l10n_ro_document_type`) to journal entries, so that the
Romanian journals and registers can show which document justifies each entry: invoice, credit note,
vendor bill, customs import declaration (DVI), cash receipt, cash disposal, bank statement, payroll,
expense report or a plain journal entry.

- Invoices and receipts take the type from the kind of document.
- Bank statement lines are *Bank Statement*. A payment in a bank journal is *Payment Order / Bank
  Document*: its entry is posted on the outstanding account, before the statement and sometimes
  without being reconciled with it, so the statement does not justify it. On cash journals both are
  *Cash Document*.
- Every other entry is a *Journal Entry* until the module that creates it says otherwise (the DVI
  entry of `l10n_ro_customs_dvi`, the cash receipts and disposals of `l10n_ro_account_sequence`).
- On a journal entry the accountant can change the type from the form, for example an import VAT
  entry recorded by hand, whose supporting document is the DVI.

The VAT purchase and sales journal of `l10n_ro_account_vat_journal` uses it for the *Document Type*
column.
