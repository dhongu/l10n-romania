## 19.0.1.0.0 (2026-11-16)

- Prima versiune: meniul *Mesaje SPV (vedere împărțită)* cu kanban și listă și panou lateral pe
  `l10n_ro_edi.document`, fără Python (Odoo Online). Documentul facturii și CUI-ul se citesc în browser
  din XML-ul facturii (DOMParser), cu teste Hoot pentru citirea XML-ului.
- Nu se instalează împreună cu `l10n_ro_message_spv_side_panel`; importul zip se oprește cu un ID
  extern lipsă (`error_uninstall_..._first`) cât timp acela e instalat.
