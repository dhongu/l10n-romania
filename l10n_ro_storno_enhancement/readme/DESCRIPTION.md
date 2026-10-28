This module extends Odoo's storno accounting for the Romanian localization: corrections
are booked "in red", with negative amounts on the same side of the account as the
original entry, so the turnover of the accounts is not inflated by a reversal on the
opposite side.

**Key features:**

- **Storno on every reversal:** standard Odoo applies storno only to credit notes, and
  only for companies where storno accounting is enabled (automatically, when Romania is
  the fiscal country). With this module, any reversed journal entry, miscellaneous
  entries included, is posted in red, and reversing a storno entry gives back a normal
  entry.
- **Manual storno on journal entries:** the "Storno (red reversal)" option on a draft
  miscellaneous entry posts all its lines in red, for corrections recorded by hand.
- **Account usage:** a "Usage" field on accounts classifies them as Activ (debit balance),
  Pasiv (credit balance) or Bifunctional (default). It is filled in automatically at
  installation for the accounts of the Romanian chart of accounts and can be changed per
  account.
- **Former name:** the module was previously called `l10n_ro_account_storno`. When it is
  installed on a database that has the former module, it takes over its data
  automatically, keeping the account usage values.
