## 20.0.0.0.8 (2026-10-29)

- Migrare pe Odoo 20:
  - dependența `stock_picking_batch` devine `stock`, unde au trecut loturile;
  - pe aviz, `t-esc` devine `t-out`;
  - unitatea mișcării se citește din `uom_id`, iar unitatea liniei de achiziție tot din
    `uom_id`; pe linia de vânzare rămâne `product_uom_id`.

## 19.0.0.0.7 (2026-10-29)

- Fișa consultant (`readme/FISA_CONSULTANT.md`) cu capturi generate din `tests/test_screenshots.py`.
- **Avizul lotului: cantitățile și valorile în unități diferite.** Cantitățile mișcărilor
  se adunau așa cum erau, deci 2 duzini + 6 bucăți ieșeau „8”, iar prețul din comandă se
  înmulțea cu cantitatea mișcării, chiar dacă linia de comandă avea altă unitate. Acum
  cantitățile se cumulează în unitatea produsului, iar valoarea se calculează în unitatea
  liniei de comandă, ca pe avizul din transfer (`l10n_ro_picking_report` 19.0.1.3.6).
- CIF-ul și NRC-ul destinatarului apar și când livrarea merge la o adresă de livrare
  (contact al firmei); condiția se verifica pe contact, nu pe firmă.
- Valorile din comenzile în altă monedă se convertesc în moneda companiei, la cursul de la
  data lotului; înainte se afișa aceeași cifră, cu simbolul monedei companiei.
- Cantitatea apare în formatul limbii, cu precizia unității de produs („15,00”, nu „15.0”).

## 19.0.0.0.6 (2026-10-22)

- Listed on Odoo Apps as *Romania - Batch Delivery Note* (was *Romania - Terrabit - Picking batch Report*), with the same title on the Apps banner.
  The technical name `l10n_ro_stock_picking_batch_report` does not change.

## 19.0.0.0.5 (2026-10-12)

- Depends on `l10n_ro_picking_report`, the new name of `l10n_ro_stock_picking_report`.

## 19.0.0.0.4 (2026-10-09)

- Delivery batch report: removed the leftover debug line that printed the list of product IDs in the PDF.

## 19.0.0.0.3 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.0.0.2 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.
