## 20.0.2.2.0 (2026-11-14)

Forward-port of 19.0.2.1.4 – 19.0.2.2.0:

- Customs regime 4200 (VAT-exempt import followed by an intra-Community supply): the import VAT
  stays empty, only the base goes to row 29 of the VAT return, and the VAT held by customs as a
  guarantee is tracked on the DVI (blocked / released), without a journal entry.
- The import VAT lines of the DVI entry are linked to the tax (SAF-T D406, VAT closing); neutral
  "Import VAT" labels for both regimes; the DVI entry is created and posted even without customs
  duty.
- The DVI landed cost is linked to the vendor bill; the foreign supplier is set on the header of the
  DVI entry (VAT purchase journal).
- Multi-company: the customs payable account (446) is taken from the chart of the DVI company.
- The DVI entry has the document type *Import (DVI)* (`l10n_ro_account_move_document_type`, new
  dependency). The entries of the DVIs already validated get the supplier and the document type on
  upgrade.
- Consultant sheet: deferred import VAT, VAT refund, regime 4200 and its sales flow.

## 20.0.2.1.3 (2026-10-13)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 20.0.2.1.2 (2026-10-04)

- Documentation and the help of the *Import VAT* field: the regime without VAT paid at customs
  (art. 326(4)-(5) of the Romanian Fiscal Code) covers all four cases — deferral certificate,
  centralised clearance, entry in the declarant's records and the goods of art. 331(2)(b), (c),
  (i)-(k) — and is described as VAT recorded both as collected and as deductible, not as reverse
  charge. The tax to choose is named: "21% IMP AM" / "11% IMP AM" from `l10n_ro_anaf_d300`, which
  also carry the VAT return rows 7 and 22.
- The deduction condition is now split by regime: proof of payment for VAT paid at customs
  (art. 299(1)(c)); for imports without payment at customs, the declaration with the importer and
  the VAT due, plus the VAT recorded as collected in the same period (art. 299(1)(d)).

## 20.0.2.1.1 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.
