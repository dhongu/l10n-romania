## 20.0.0.4.2 (2026-10-29)

- Migrare pe Odoo 20: trimiterea din lot vine acum din `l10n_ro_edi_stock`, deoarece
  `l10n_ro_edi_stock_batch` nu mai există.
- **Metoda de livrare a lotului** se calcula din transferurile primului lot din selecție,
  nu din ale lotului curent. Într-o listă cu mai multe loturi, toate primeau aceeași metodă.
  Câmpul nu avea nici `@api.depends`, deci nu se recalcula când se schimbau transferurile.
- **Transportatorul eTransport** al lotului se golește când lotul rămâne fără transferuri.
  Înainte păstra valoarea veche.

## 19.0.0.4.1 (2026-10-29)

- Fișa consultant (`readme/FISA_CONSULTANT.md`) cu capturi generate din `tests/test_screenshots.py`.
- Traducerea în română (`i18n/ro.po`) refăcută pentru acest modul: era copiată de la
  `l10n_ro_etransport_enhancement`, iar etichetele lotului (transportator, greutăți, butoane)
  apăreau în engleză.
- Bifa „Greutăți de transport măsurate” de pe lot își afișează din nou eticheta, iar blocul
  de greutăți are titlul „Greutăți cântărite”, ca să nu se confunde cu locațiile.
- Pe avizul lotului, UIT-ul e separat de etichetă printr-un spațiu.

## 19.0.0.4.0 (2026-10-29)

**Fix — declarația pe lot ignora greutățile cântărite și documentele lotului.**
`l10n_ro_edi_stock_batch` construiește declarația lotului pe un `stock.picking`
gol, deci override-urile `_l10n_ro_edi_stock_get_template_data` și
`_l10n_ro_edi_stock_validate_data` definite pe `stock.picking.batch` nu rulau
niciodată. XML-ul pleca tăcut cu greutățile calculate de nucleu și un singur
aviz cu numele lotului: liniile de greutate și CMR-ul lotului nu ajungeau la ANAF.
Lotul e acum dedus din mișcările declarate (hook-ul
`_l10n_ro_etransport_declaration_record` din `l10n_ro_etransport_enhancement`),
iar greutățile cântărite, documentele lotului și ale transferurilor din el și
marcajul post-avarie ajung în declarație. Override-urile moarte au fost eliminate.

**Nou:** bifa „Post-outage Declaration” pe lot.

## 19.0.0.3.5 (2026-10-22)

- Listed on Odoo Apps as *e-Transport for Transfer Batches* (was *eTransport Batch Enhancement*). The technical name `l10n_ro_etransport_batch_enhancement` does not change.

## 19.0.0.3.4 (2026-10-12)

- Depends on `l10n_ro_picking_report`, the new name of `l10n_ro_stock_picking_report`.

## 19.0.0.3.3 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.0.3.2

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.

## 19.0.0.3.1

**Corecție** — la fel ca în `l10n_ro_etransport_enhancement`, documentele însoțitoare
declarate pe lot fără observație generau `observatii=""` în XML, respins de ANAF
(`Str200`, minLength=1). Atributul este acum omis când observația lipsește.
