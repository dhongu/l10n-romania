## 19.0.1.3.4 (2026-09-22)

- **NIR: cantitatea și prețul de vânzare rămâneau în unitatea de referință.**
  Continuarea fixului din 19.0.1.3.3, care adusese doar prețul de achiziție pe
  unitatea documentului. Mai rămâneau trei locuri în aceeași familie de erori:
  coloana „Cantitate" tipărea `move.product_qty` (cantitatea convertită în unitatea
  de referință) etichetată cu unitatea documentului — recepția de 10 cutii a 13 kg
  se citea „130 Cutie × 37,70 = 377,00", cu valoarea corectă lângă o cantitate care
  nu se potrivea cu ea; coloana „Preț vânzare" rămânea per kg lângă un preț de
  achiziție per cutie; iar recepțiile **fără comandă de achiziție** (inclusiv nota
  de transfer) înmulțeau un preț per unitate de document cu `move.product_qty`.
  Acum toate coloanele se exprimă în unitatea de pe document. Ca și înainte, cazul
  apare doar cu `stock.propagate_uom = 1`.
  Rapoartele de livrare (`report_delivery_price`) au aceeași problemă la calculul
  din comanda de vânzare — se tratează separat.

## 19.0.1.3.3 (2026-09-22)

- **NIR: sumă greșită când unitatea de pe document diferă de cea de referință.**
  Prețul de pe mișcarea de stoc (`move.price_unit`) este exprimat în unitatea de
  referință a produsului, iar cantitatea în unitatea de pe document. Raportul le
  înmulțea ca atare, deci coloana „Valoare" ieșea mai mică cu exact factorul
  unității, în timp ce coloana „Preț unitar" — convertită separat, la final —
  arăta corect. O recepție de 1.344 de cutii a 13 kg, la 2,90 lei/kg, afișa
  3.897,60 lei în loc de 50.668,80. Conversia se face acum înaintea calculului
  taxelor, iar cantitatea de rezervă folosește unitatea documentului.
  Cazul apare doar cu `stock.propagate_uom = 1`; în configurația implicită Odoo
  convertește mișcarea în unitatea de referință, deci preț și cantitate ajung
  amândouă în aceeași unitate și eroarea nu se vede.

## 19.0.1.3.2 (2026-08-15)

- Imp: `stock.picking.delegate_id` is now indexed. The same field is declared in `deltatech_cmr_document`, so the attribute is set in both modules — the last one loaded decides.
  Context: `res_partner` is referenced by ~158 foreign-key columns; on a production database 77 of them had no index, so a single partner deletion triggered sequential scans over 3.180 MB of tables. Deleting 5.350 merged partner records took over 8 minutes without indexes and 190 seconds with them, foreign keys left ENABLED.

## 19.0.1.3.1

- **Fix:** internal transfer report no longer crashes with
  `ZeroDivisionError` when a move has only the done quantity filled in
  (`quantity`) and no demand (`product_uom_qty`), which leaves
  `product_qty` at 0. The unit price now falls back to `quantity` and the
  division is skipped entirely when both quantities are 0. The previous
  `or 1` fallback applied to the division result, not the denominator, so
  it never protected against this case.

## 19.0.1.2.10

- **Fix:** reception report no longer crashes on Odoo 19. `stock.picking` lost
  the `group_id` field (the procurement group mechanism was replaced by
  `stock.reference` / `reference_ids`), which raised
  `AttributeError: 'stock.picking' object has no attribute 'group_id'` when
  printing reception NIRs. The shared `report_reception_text` template now
  branches on field existence so it renders correctly for both `stock.picking`
  (`reference_ids`) and the `stock.picking.cumulative` report model (`group_id`).
