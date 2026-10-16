# Self-Billing Message SPV (Romania)

At self-billing (Cod fiscal art. 319 (18)) the customer issues the invoice in
the supplier's name and reports it to the SPV. The legal number of such a
document is the one the customer allocated, not one from the supplier's own
sequence — and using the regular sales sequence also breaks it, because these
documents arrive days after the invoices already issued and are dated back.

This addon adds a **Number from SPV message** flag on sales and purchase
journals. On a journal with the flag set, matching a draft with its SPV
message fills the document number from the reference of the message.

## Key features

- New option on `account.journal`: *Number from SPV message*, off by default.
- At matching (`Find invoice`), a draft in such a journal is numbered with the
  reference of the SPV message instead of the journal sequence.
- Posted documents are never renumbered.
- A number already used in the journal is skipped and logged, since posting
  would fail on the unique number constraint.
