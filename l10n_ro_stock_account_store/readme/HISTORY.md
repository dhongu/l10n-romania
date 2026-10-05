## 20.0.1.0.0 (2026-10-05)

- Migration to 20.0. Odoo 20 signs the value of the stock move (negative on the
  outgoing moves): the markup is computed on its magnitude, so the store entries
  are the same as on 19.0.
- The upgrade script `19.0.1.0.0` is kept: it also runs on a direct upgrade from
  18.0 to 20.0.

## 19.0.1.0.0 (2026-10-04)

- Migration to 19.0, rewritten on the stock move: Odoo 19 no longer has
  `stock.valuation.layer`, so the markup (378) and uneligible VAT (4428) entry is
  now a separate journal entry linked to the stock move, built on the move types
  of `l10n_ro_stock_account`.
- The `Romania - Merchandise type` field of the location moves here from
  `l10n_ro_stock` (same column, the value is kept at upgrade).
- New `Romania - Store Markup Account` on the product category, instead of the
  price difference account removed from Odoo 19. At upgrade, a 378 account set as
  price difference account is carried over.
- Optional `Romania - Store Uneligible VAT Account` on the product category, so
  the 4428 of the store can be kept apart from the VAT on payment.
- A move leaving the store releases markup and VAT at the sale price of the last
  entry in that store (shelves included), instead of the current price of the product, so 378 and
  4428 close. Returns reverse in red the entry of the returned move.
- The sale amount kept on the valuation layers in 18.0 is moved to the stock move
  at upgrade.
- Store filter and merchandise type column on the locations list.
- With `l10n_ro_stock_picking_report`, a store location prints again the NIR at
  sale price.
- Automated tests.
