## 19.0.0.4.0 (2026-10-07)

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

## 19.0.0.3.2

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.

## 19.0.0.3.1

**Corecție** — la fel ca în `l10n_ro_etransport_enhancement`, documentele însoțitoare
declarate pe lot fără observație generau `observatii=""` în XML, respins de ANAF
(`Str200`, minLength=1). Atributul este acum omis când observația lipsește.
