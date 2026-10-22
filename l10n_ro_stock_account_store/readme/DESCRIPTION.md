Stock accounting for goods kept at sale price (retail store), for Romanian
companies.

A location marked as **Store** (`Romania - Merchandise type`) keeps its goods at
sale price, VAT included. Every move that enters or leaves such a location gets,
next to the usual stock entry at cost, a separate journal entry for the trade
markup (378) and for the uneligible VAT (4428).

1. Goods received from a supplier, with invoice:

   - 371 = 401 (cost) and 4426 = 401 (VAT), from the vendor bill
   - markup: 371 = 378
   - uneligible VAT: 371 = 4428

2. Goods received from a supplier with a delivery note (no invoice yet):

   - at reception: 371 = 408, then 371 = 378 and 371 = 4428
   - when the invoice arrives: 408 = 401 and 4426 = 401

3. Goods moved from a depot (at cost) to the store: the internal transfer at
   cost, then 371 = 378 and 371 = 4428.

4. Goods leaving the store (delivery, consumption, inventory loss, transfer to
   a depot): 378 = 371 and 4428 = 371, next to the exit at cost.

5. Returns (to the supplier, from the customer) reverse in red (storno) the
   markup and VAT entry of the returned move, at its sale price.

The sale price is taken from the product (`Sales Price` and `Customer Taxes`)
when the goods enter the store. A move leaving the store releases markup and VAT
at the sale price of the last entry of the product in that store, or of its last
revaluation when it is newer. The amounts are kept on the stock move (`Store Sale
Amount`, `Store Markup`, `Store Uneligible VAT`).

6. Sale price change: when the sale price of a product changes (`Sales Price` of the
   product or the extra price of a variant), the stock of every store where the
   store price changed is revalued at once, on the date of the change, with a
   numbered **Store Revaluation** (*Inventory > Reporting > Store Revaluations*):

   - the old value is the sale value booked for the product in that store (entries,
     exits and previous revaluations), the new value is the booked quantity x new
     price, VAT included, so the residual balances left until then by entries at
     different prices are cleared; stock put in the store without a store entry
     (e.g. before the module) has no markup and is not revalued;
   - price increase: 371 = 378 (difference without VAT) and 371 = 4428 (VAT
     difference);
   - price cut: the reverse entry in black, 378 = 371 and 4428 = 371;
   - a price cut below the unit cost (product cost) is refused while there is stock
     in the store: a sale below cost is an impairment of the stock at cost (6814 =
     397), which does not unlock the price change. Receptions in the store are not
     blocked by this rule;
   - a change on a date in a locked period is refused; the entry is never moved to
     another date;
   - a store with its own pricelist takes its price from the pricelist, so a change
     of the product price revalues it only when the store price changes;
   - a return (from a customer or to the supplier) moves the goods at the price of
     the move it returns; right after it, the rest of the store stock is brought
     back to the current store price with a revaluation linked to the return;
   - the exit that empties the stock booked in the store releases exactly the markup
     and the VAT left, so no cents remain on 378 / 4428.

Limitations, to be handled outside the module:

- a change made only in the pricelist of a store, or a change of the VAT rate of
  the product, is not revalued at the time of the change; the first return in that
  store afterwards brings the stock to the new store price;
- the impairment of the stock at cost (6814 = 397) is booked outside the module; it
  does not allow a sale price below cost while the goods are in the store;
- a transfer between two stores moves no markup or VAT: the store left keeps the
  quantity and the sale value booked, and the goods are not booked at sale price in
  the store of destination, so a revaluation of either store is wrong until the
  goods leave it;
- the stock already in a store when the module is installed has no store entry: book
  it first at sale price with an opening entry 371 = 378 / 4428, otherwise its exit
  leaves equal and opposite amounts on 371 and 378;
- when the vendor bill comes with another cost than the reception, the stock
  value is corrected (371 = 401), but the markup booked at reception is not, so
  the difference has to be regularised on 378 manually.

Out of scope: monthly release of the markup with the K coefficient, sales
through the Point of Sale, the printed price change report (minutes) and the store inventory
report at sale price.
