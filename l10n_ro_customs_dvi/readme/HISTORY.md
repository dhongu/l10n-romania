## 19.0.2.1.8 (2026-10-16)

- New *Customs Regime* field on the DVI wizard and on the landed cost (4000 / 4200 / other).
  Under regime 4200 (import exempt from VAT, art. 293(1)(m) of the Romanian Fiscal Code, followed
  by an intra-Community supply) the wizard proposes the exempt tax "0% EXEMPT" with no import
  VAT, and the DVI entry carries only the base, on row 29 of the VAT return (D300), through the
  technical 473 pair. Until now an import without VAT left no trace in the VAT return. The VAT
  held by customs as a guarantee is not recorded on the DVI; a 4200 DVI with import VAT is
  refused.
- When the DVI has no customs duty, the entry created for the import VAT (or the exempt base) is
  now posted; it used to stay in draft and was left out of the VAT return.

## 19.0.2.1.7 (2026-10-16)

- The landed cost created by the DVI wizard is now linked to the supplier invoice through the
  standard *Vendor Bill* field, which was left empty: the field shows the invoice, the invoice gets
  the *Landed Costs* smart button and the stock valuation details name the invoice. Landed costs
  created before this version keep the field empty.

## 19.0.2.1.6 (2026-10-16)

- Neutral labels for the import VAT, valid in both regimes: the journal items of the DVI entry are
  now labelled "Import VAT - <tax>" and the amount field "Import VAT Amount". The old label "VAT
  paid at customs" was also used for imports without VAT paid at customs ("21% IMP AM" /
  "11% IMP AM") and reached the general ledger and SAF-T (D406). Entries already posted keep the
  old label.

## 19.0.2.1.5 (2026-10-16)

- Consultant sheet: step-by-step flow for imports without VAT paid at customs (art. 326(4)-(5) of
  the Romanian Fiscal Code, "21% IMP AM" / "11% IMP AM" taxes), with two new screenshots; the
  reporting notes now cover D406 (SAF-T); new section on the refund of VAT paid at customs, with
  the cases that have a legal basis, the journal entries and a request template (Annex A).

## 19.0.2.1.4 (2026-10-16)

- SAF-T (D406): the VAT lines of the DVI entry are now linked to the tax (tax distribution line),
  and the technical base line carries the tax. The VAT paid at customs (and the deductible part of
  "21% IMP AM" / "11% IMP AM") was exported with TaxType 000 / TaxCode 000000 and TaxAmount 0.
  The VAT return tags (rows 24/25, 7/22) are unchanged; the Odoo VAT closing now also takes the
  DVI VAT into account.

## 19.0.2.1.3 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.2.1.2 (2026-10-04)

- Documentation and the help of the *Import VAT* field: the regime without VAT paid at customs
  (art. 326(4)-(5) of the Romanian Fiscal Code) covers all four cases — deferral certificate,
  centralised clearance, entry in the declarant's records and the goods of art. 331(2)(b), (c),
  (i)-(k) — and is described as VAT recorded both as collected and as deductible, not as reverse
  charge. The tax to choose is named: "21% IMP AM" / "11% IMP AM" from `l10n_ro_anaf_d300`, which
  also carry the VAT return rows 7 and 22.
- The deduction condition is now split by regime: proof of payment for VAT paid at customs
  (art. 299(1)(c)); for imports without payment at customs, the declaration with the importer and
  the VAT due, plus the VAT recorded as collected in the same period (art. 299(1)(d)).

## 19.0.2.1.1 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.
