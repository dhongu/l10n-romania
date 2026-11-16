## 19.0.1.0.1 (2026-10-30)

- Tests: the test partner gets a full Romanian address, so the posted customer invoices pass the
  address check of `l10n_ro_efactura_enhancement` when both modules are installed (CI).

## 19.0.1.0.0 (2026-10-29)

- New module (helpdesk ticket #9568): document type on journal entries, filled in automatically for
  invoices, receipts and payments and editable on journal entries. Existing entries are filled in
  at installation directly in SQL (`pre_init_hook`), without recomputing the field in Python.
- A payment in a bank journal is *Payment Order / Bank Document*: its entry is posted on the
  outstanding account and is justified by the payment order, not by the statement. Only the entries
  of bank statement lines are *Bank Statement* (Pacioli review).
- Consultant sheet (`readme/FISA_CONSULTANT.md`) with screenshots.
