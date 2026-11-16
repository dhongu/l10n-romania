The module adds two controls that protect the stock accounting entries.

**1. Storable product lines must come from an order (optional)**

Go to **Invoicing → Configuration → Settings**, open **România** in the left panel and tick
**Check storable product line source**, then **Save**. The option applies to the whole database.

![Settings, România section: the option Check storable product line source is ticked and highlighted](static/description/en/01_setare_verificare_sursa.png)

With the option on, a customer invoice or credit note with a storable product that does not come
from a sales order cannot be confirmed: **Confirm** shows "Invoice line with storable product '...'
must have a reference to a sales order line." Invoice from the sales order instead.

![Draft customer invoice without a sales order and the Invalid Operation dialog about the missing sales order line](static/description/en/02_factura_client_fara_comanda.png)

Vendor bills and refunds work the same way: a storable product line must come from a purchase order
(fill the bill from the purchase order with **Auto-Complete**).

![Draft vendor bill without a purchase order and the Invalid Operation dialog about the missing purchase order line](static/description/en/03_factura_furnizor_fara_comanda.png)

Lines with services or consumables are not checked.

**2. Stock moves must have a unit price (always on)**

When Odoo computes the unit price of real stock moves and gets 0, the operation stops with
"Price unit is not set for product ...". For example, validating the delivery of a FIFO product
without cost from a sales order (with the sales margin module installed) is blocked, and the
delivery stays **Ready**. Set the product cost, or receive the goods with a price, then validate
again.

![Delivery of a product without cost and the Invalid Operation dialog: Price unit is not set for product](static/description/en/04_livrare_pret_zero.png)

Computations on an empty set of moves (for example, the returns of a delivery that has none) are
not checked.

**System parameters**

In developer mode, **Settings → Technical → Parameters → System Parameters** shows
`l10n_ro_stock_account.check_storable_line_source` (written by the setting above) and, if created,
`l10n_ro_stock_account.skip_price_unit_check`. Set the latter to `True` only to allow moves without
cost temporarily (for example, an opening stock at zero cost), then back to `False`.

![System Parameters filtered on the l10n_ro_stock_account keys](static/description/en/05_parametri_sistem.png)
