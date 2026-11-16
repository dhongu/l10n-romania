## 19.0.1.0.2 (2026-11-16)

- Am pus înapoi `__init__.py` gol: uneltele OCA (manifestoo, oca-checks-odoo-module) nu
  recunosc un modul fără el, așa că pica CI-ul suitelor care depind de acest modul.
  Modulul tot nu are cod Python și se importă în continuare pe Odoo Online.
- Marcaj Odoo Online explicit: `"online": true` în `static/description/banner.json`
  (bannerul nu îl mai deduce din lipsa fișierelor `.py`).

## 19.0.1.0.1 (2026-11-14)

- Cannot be installed together with `l10n_ro_message_spv`, the module with Python code that does the same
  thing: the manifest lists it under `excludes`.
- The zip import (Apps > Import Module) does not check `excludes`, so the import now stops with a
  missing external ID (`error_uninstall_..._first`) while that module is installed.

# 19.0.1.0.0

- First version: *SPV Messages* register over `l10n_ro_edi.document` (list, filters, form with
  the XML and the files of the invoice), **Synchronize now**, no Python (Odoo Online).
- Consultant sheet (`readme/FISA_CONSULTANT.md`), `readme/USAGE.md` and screenshots (RO, EN).
