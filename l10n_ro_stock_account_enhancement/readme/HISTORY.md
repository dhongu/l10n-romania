## 20.0.0.0.6 (2026-11-16)

**Changed**

- Apps Store page (`static/description/index.html`) regenerated with the Terrabit template.

## 20.0.0.0.5 (2026-11-16)

- Fișa consultant (`readme/FISA_CONSULTANT.md`), portată de pe 19.0 și adaptată la Odoo 20, cu capturi generate automat (`tests/test_screenshots.py`), în română și în engleză, plus GIF-ul demo.
- `readme/USAGE.md` nou, în engleză.

## 20.0.0.0.4 (2026-11-16)

- Corectare: validarea livrărilor din comenzi de vânzare nu mai eșuează cu „Price unit is not set for product ...”. Cu `sale_stock_margin` instalat, recalcularea costului pe linia comenzii (`_get_price_unit_delivery(product=...)`) apela `_get_price_unit` pe un recordset gol de mișcări. Verificarea prețului rămâne activă pentru mișcările reale.

## 20.0.0.0.3 (2026-10-22)

- Listed on Odoo Apps as *Romania - Stock Accounting Controls* (was *Romania - Stock Accounting Enhancement*), with the same title on the Apps banner.
  The technical name `l10n_ro_stock_account_enhancement` does not change.

## 20.0.0.0.2 (2026-10-15)

- Migrare la Odoo 20: `stock.move._get_price_unit` primește noua semnătură
  (`product`, `include_consigned`, `include_consumable`). În 20.0 costul vânzării (COGS) de pe
  factură trece și el prin această metodă (în 19.0 folosea `_get_cogs_price_unit`), așa că
  apelul cu `include_consigned=True` nu este verificat, ca înainte.
- Parametrii de sistem se citesc cu `get_bool` (în 20.0 `get_param` nu mai există).
- Teste noi pentru verificarea prețului unitar, cu notele contabile Dr/Cr ale recepției cu
  aviz (371 / 408) și ale livrării (607 / 371).
- Traducerea în română a mesajului „Price unit is not set for product”.

## 19.0.0.0.2 (2026-10-09)

- Banner pentru Odoo Apps (`static/description/main_screenshot.png`), generat din `banner.json`.

## 19.0.0.0.1 (2026-09-30)

- Iconiță proprie a modulului, în stilul plat al modulelor Terrabit, în locul celei lipsă sau generice.
