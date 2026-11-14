# 20.0.1.0.1 (2026-11-14)

- Cannot be installed together with `l10n_ro_message_spv`, the module with Python code that does the same
  thing: the manifest lists it under `excludes`.
- The zip import (*Apps > Import Module*) does not check `excludes`: a guard on the first field
  stops it while `l10n_ro_message_spv` is installed.

# 20.0.1.0.0

- Migration to 20.0: no change in the data; **Synchronize now** opens first the standard window that
  asks for the period to synchronize (`l10n_ro_edi.account_move_fetch_invoices.wizard`, up to 60
  days back).

# 19.0.1.0.0

- First version: *SPV Messages* register over `l10n_ro_edi.document` (list, filters, form with
  the XML and the files of the invoice), **Synchronize now**, no Python (Odoo Online).
- Consultant sheet (`readme/FISA_CONSULTANT.md`), `readme/USAGE.md` and screenshots (RO, EN).
