This is a technical add-on for the OCA storage sheet report (`l10n_ro_stock_report`, on the OCA
valuation engine `l10n_ro_stock_account`). There is no menu or setting of its own.

1. Sell a product with the *Dropship* route, confirm the generated purchase order and validate
   the dropship transfer (`DS/…`) when the goods reach the customer.

   ![Done dropship transfer from the vendor, operation type Dropship, with the product line](static/description/en/01_transfer_dropship.png)

   The OCA valuation engine posts the transfer entry *607 = 371* at the purchase value; the
   vendor bill posts *371 + 4426 = 401*.

   ![Journal entry of the dropship transfer: 607000 debit and 371000 credit, 3,000.00 each](static/description/en/02_nota_dropship.png)

2. Open **Inventory > Reporting > Romanian Stock Sheet Report**, choose the location and the
   period and click **Show Sheet**: in the list view the dropship transfer shows as an input and
   an output row with the same quantity and amount.

   ![Storage sheet list with the dropship transfer as one input and one output row of the same amount](static/description/en/03_lista_fisa_dropship.png)

3. **Show Sheet Pdf** prints the dropship rows under the stock account of the product category
   (e.g. 371000); after both rows the stock is back to its previous value.

   ![Printed storage sheet with the dropship input and output rows under the 371000 account](static/description/en/04_pdf_fisa_dropship.png)
