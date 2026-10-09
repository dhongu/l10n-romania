## 19.0.0.3.3 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.0.3.2

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.

## 19.0.0.3.1

**Corecție** — la fel ca în `l10n_ro_etransport_enhancement`, documentele însoțitoare
declarate pe lot fără observație generau `observatii=""` în XML, respins de ANAF
(`Str200`, minLength=1). Atributul este acum omis când observația lipsește.
