1. Go to *Inventory > Configuration > Settings*, section **UIT**:
   - **Get UIT prices from sale/purchase orders**: when enabled, the e-Transport document pulls the goods' declared value from the linked sale/purchase order instead of the stock valuation.
   - **Get only validated quantity from the picking instead of picking quantity**: shown only when the above is enabled; use it to report the actually validated (done) quantity to ANAF rather than the demanded quantity.
2. On a stock picking (*Inventory > Transfers*), next to the carrier field you can now also fill in a **Transport Partner** even if no delivery **Carrier** is set — the picking can be validated for e-Transport with either one filled in, not both.
3. On the *e-Transport* tab of the picking, enable **Shipping weights** to manage weights at line level:
   - Click **Get lines** to populate the weight lines from the picking's stock moves.
   - Edit net/gross weight per line, or click **Distribute weights** to spread a total net/gross weight proportionally across all lines.
   - If a stock move gets reserved *after* the lines were generated (e.g. quantity was 0 when you clicked **Get lines**), it stays without a weight line. A red warning above the list tells you how many moves are missing a line so you can click **Get lines** again before sending.
4. Validate and send the e-Transport document as usual (via `l10n_ro_edi_stock`); the corrected quantities/weights and the manual transport partner are used automatically when building the ANAF submission, avoiding rejections for missing `cantitate`/`greutateBruta` attributes on zero-quantity or zero-weight lines.
