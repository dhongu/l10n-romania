## 18.0.0.1.2 (2026-10-22)

- Listed on Odoo Apps as *Revolut MT940 Statement Import* (was *MT940 Revolut Format Bank Statements Import*). The technical name `l10n_ro_account_bank_statement_import_mt940_revolut` does not change.

## 18.0.0.1.1 (2026-09-04)

- Fix: `_revolut_journal_exists` looked up the matching journal by IBAN alone
  (`limit=1`, no currency filter), so it always returned the first journal
  found on that IBAN regardless of which currency wallet was being checked.
  With a single journal per IBAN this happened to work, but as soon as a
  second journal (a different currency) is linked to the same IBAN - the
  intended way to import all of a Revolut account's currency wallets - every
  wallet other than the first journal's currency was silently dropped as
  "no matching journal", even though one existed. The lookup now checks all
  journals sharing that IBAN. Ticket #9408 (Agroamat).

## 18.0.0.1.0

- Initial version: MT940 parser for Revolut Business exports (multiple
  currency-wallet blocks under the same IBAN), matching each wallet to its
  own bank journal.
