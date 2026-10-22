## 20.0.1.1.1 (2026-10-22)

- Odoo Apps banner title: *Stock Accounting Store* (was *Retail Store Stock Accounting*), the same as the module name.

## 20.0.1.1.0 (2026-10-22)

- Sale price change: changing the sale price of a product (or the extra price of a variant)
  revalues at once the stock of every store where the store price changed, with a numbered
  **Store Revaluation** and its entry: 371 = 378 / 4428 for an increase, the reverse in black
  (378 / 4428 = 371) for a price cut. The old value is the sale value booked in the store, so
  the residual balances of 378 and 4428 left by entries at different prices are cleared.
  Before, a price change had no entry and the next exit released markup and VAT at the price of
  the last entry, leaving the difference on 378 / 4428.
- The exits after a revaluation release markup and VAT at the revalued price.
- A price cut below the unit cost is refused (impairment 6814 = 397, outside the module), and so
  is a change in a locked period: the entry keeps the date of the price change.
- After a return to or from the store, which moves the goods at the price of the returned move,
  the rest of the store stock is brought back to the current store price.
- The exit that empties the stock booked in the store releases exactly the markup and VAT left.
- An exit dated before a revaluation leaves at the price of its date.
- Ported from 19.0.1.1.0.

## 20.0.1.0.2 (2026-10-13)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`, with the Odoo 20 badge.

## 20.0.1.0.1 (2026-10-05)

- The markup (378) and uneligible VAT (4428) of a reception in the store now use the same sale
  price as the reception note at sale price (NIR) of `l10n_ro_stock_picking_report`: the price
  frozen on the move at reception, else the store pricelist of the location, else the product
  price. Before, the entry always took the product price, so in a store with its own pricelist the
  NIR showed one markup and VAT and the accounts 378 / 4428 another (e.g. store price 120 instead
  of 100: NIR markup 600, entry 400).
- Tests: the NIR at sale price matches the store entry, with and without a store pricelist.

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
