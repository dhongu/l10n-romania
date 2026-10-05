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
