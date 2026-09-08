Checks that the stock valuation agrees with the general ledger, and helps fix
the differences it finds.

For each product and stock valuation account it compares two figures:

* the **valuation** carried by the done stock moves (`stock.move.value`, signed
  according to the Romanian move type), and
* the **accounting** balance posted on that account (`account.move.line`).

The two are written by different documents in the Romanian localization - a
reception posts no stock entry at all, the debit on 371 comes from the vendor
bill - so they can drift apart. The report lists the products where they do,
together with the cost price, the last purchase price and the quantities on
both sides.

From the result list you can:

* drill down to the stock moves and to the journal items behind each figure,
* re-post the accounting entry of a move (*Correction Valuation*),
* post an adjustment journal entry (*Fix AML*),
* book an inventory adjustment carrying the missing value (*Fix Valuation*),
* move the valuation of a product onto the account its category defines,
* align the cost price with the last purchase price.

It also flags receptions without a vendor bill, deliveries without a customer
invoice, and journal entries dated differently from their stock move.
