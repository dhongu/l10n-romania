Install the module when the company does not use the net weight of the products. There
is nothing to configure.

1. Go to **Inventory → Products → Products**, open a product and the **Inventory** tab.
   The **Logistics** group shows **Weight** and **Volume** one under the other: the **Net Weight** field
   added by `l10n_ro_stock_base` is hidden, on the product and on the product variant
   forms. Enter the product weight in **Weight**, the gross weight used for transport.

   ![The Inventory tab of a product: the Logistics group shows Weight and Volume, highlighted, without the Net Weight field](static/description/en/01_produs_fara_greutate_neta.png)

The field is only hidden: the values already saved stay in the database, can be exported
from the product list and show again if the module is uninstalled.

If the company uses the shipping weight lines of `l10n_ro_etransport_enhancement`, the
net weight of the products is still used for the net weight of the e-Transport
declaration, even when hidden. Clear the saved net weights first (export, set to 0,
import; for products with variants, from **Inventory → Products → Product Variants**),
or do not install this module.
