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
at the sale price of the last entry of the product in that store, so 378 and 4428
close even if the product price changed in between. The amounts are kept on the
stock move (`Store Sale Amount`, `Store Markup`, `Store Uneligible VAT`).

Limitations, to be handled outside the module:

- a change of the sale price of goods already in the store needs a price change
  report (371 = 378 / 4428 for the difference on the stock on hand); without it,
  goods entered at different prices leave residual balances on 378 and 4428;
- when the vendor bill comes with another cost than the reception, the stock
  value is corrected (371 = 401), but the markup booked at reception is not, so
  the difference has to be regularised on 378 manually.

Out of scope: monthly release of the markup with the K coefficient, sales
through the Point of Sale, sale price change reports and the store inventory
report at sale price.
