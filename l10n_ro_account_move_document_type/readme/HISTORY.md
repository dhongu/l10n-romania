## 19.0.1.0.0 (2026-10-29)

- New module (helpdesk ticket #9568): document type on journal entries, filled in automatically for
  invoices, receipts and payments and editable on journal entries. Existing entries are filled in
  at installation directly in SQL (`pre_init_hook`), without recomputing the field in Python.
- Consultant sheet (`readme/FISA_CONSULTANT.md`) with screenshots.
