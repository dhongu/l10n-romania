## 19.0.0.0.6 (2026-11-16)

**Changed**

- Apps Store page (`static/description/index.html`) regenerated with the Terrabit template.

## 19.0.0.0.5 (2026-11-16)

- Fișa consultant (`readme/FISA_CONSULTANT.md`), cu capturi generate automat (`tests/test_screenshots.py`), în română și în engleză, plus GIF-ul demo.
- `readme/USAGE.md` nou, în engleză; `readme/DESCRIPTION.md` corectat: opțiunea este în Setări → România, blocul Contabilitate.
- Traducerea în română a mesajului „Price unit is not set for product”.

## 19.0.0.0.4 (2026-11-16)

- Corectare: validarea livrărilor din comenzi de vânzare nu mai eșuează cu „Price unit is not set for product False”. Cu `sale_stock_margin` instalat, recalcularea costului pe linia comenzii (`_get_price_unit_delivery`) apela `_get_price_unit` pe mișcările de retur, de obicei un recordset gol. Verificarea prețului rămâne activă pentru mișcările reale.

## 19.0.0.0.3 (2026-10-22)

- Listed on Odoo Apps as *Romania - Stock Accounting Controls* (was *Romania - Stock Accounting Enhancement*). The technical name `l10n_ro_stock_account_enhancement` does not change.

## 19.0.0.0.2 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.0.0.1 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.
