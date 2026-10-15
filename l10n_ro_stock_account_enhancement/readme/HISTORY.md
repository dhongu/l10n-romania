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
