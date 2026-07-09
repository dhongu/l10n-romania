1. Open a transfer batch (*Inventory > Batch Transfers*, model `stock.picking.batch`).
2. On the batch form, tick **e-Transport Required** if it isn't already set from the individual pickings. Two fields appear:
   - **Carrier** (`delivery.carrier`): set once at batch level and it is propagated to every picking in the batch.
   - **Transport Partner**: the carrier/transporter company reported to ANAF; also propagated to all component pickings.
3. On the *e-Transport* tab, enable **Shipping weights** to manage weights at batch level:
   - Click **Get lines** to pull in the transfer lines (product moves) from all pickings in the batch.
   - Adjust net/gross weight per line if needed, then click **Distribute weights** to spread the batch's total net/gross weight proportionally across all lines.
   - If a stock move gets reserved *after* the lines were generated (e.g. quantity was 0 when you clicked **Get lines**), it stays without a weight line. A red warning above the list tells you how many moves are missing a line so you can click **Get lines** again before sending.
4. When the batch's e-Transport document is validated and sent to ANAF, the transport partner set on the batch is used automatically instead of requiring it on each picking.
5. The batch delivery report (from `l10n_ro_stock_picking_batch_report`) now prints the ANAF **UIT** number once the e-Transport document is validated.
