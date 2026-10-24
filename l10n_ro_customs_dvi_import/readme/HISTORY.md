## 19.0.1.0.0 (2026-10-24)

- New module: the DVI wizard of the supplier bill is filled in from the customs import declaration
  printed by the National Import System (SNI): MRN and acceptance date, customs regime, customs
  duty (A00), import VAT and its base (B00), or the VAT guarantee under regime 4200. Until now every
  value was copied by hand from the PDF. The declaration is checked before anything is filled in
  (SNI document, importer = current company, not already recorded, articles and totals consistent)
  and is attached to the DVI.
