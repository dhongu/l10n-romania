## 19.0.1.0.1 (2026-10-24)

- A declaration whose articles have different VAT rates is now refused, instead of being filled in
  with a single tax: the whole import VAT went on the VAT return row of one rate. The consultant
  sheet describes the manual procedure, one DVI per rate.
- Consultant sheet with screenshots: uploading the SNI PDF, the values read under regimes 4000 and
  4200, the DVI with the declaration attached, the journal entry and the refused duplicate.
- The *Read from the Declaration* box shows the dates and amounts in the user's language format
  (it showed `2026-09-11` and `9093.12`), and the payment method as "B00: method D, payment type 1"
  instead of "B00 D (1)".

## 19.0.1.0.0 (2026-10-24)

- New module: the DVI wizard of the supplier bill is filled in from the customs import declaration
  printed by the National Import System (SNI): MRN and acceptance date, customs regime, customs
  duty (A00), import VAT and its base (B00), or the VAT guarantee under regime 4200. Until now every
  value was copied by hand from the PDF. The declaration is checked before anything is filled in
  (SNI document, importer = current company, not already recorded, articles and totals consistent)
  and is attached to the DVI.
- Installation note: on a server with an older `cryptography` (Ubuntu 22.04 packages), installing
  `pdfminer.six` upgrades it and breaks pyOpenSSL; keep the installed version and let pip pick a
  compatible `pdfminer.six`.
