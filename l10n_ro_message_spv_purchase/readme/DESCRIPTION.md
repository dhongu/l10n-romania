# SPV Messages to Purchase Orders (Romania)

This addon extends the Romanian SPV message model (`l10n.ro.message.spv`) to link
vendor bills received through e-Factura with Purchase Orders (PO), copy the SPV
XML on the PO and link the bill lines to the PO lines, so the PO is not invoiced
twice.

## Key features

- New fields on the SPV message:
  - `Purchase Reference` (`purchase_ref`) – extracted automatically from the XML
    at `OrderReference/ID` when available.
  - `Purchase Order` (`purchase_order_id`) – the linked PO, if any.
- Two buttons on the SPV message form, shown only on purchase messages
  (vendor bills and vendor receipts):
  - *Găsește Comanda* (Find Order): searches purchase orders by reference
    (`purchase_ref`, or `ref` as fallback) in the vendor reference, source
    document or order number, restricted to the message partner and company and
    to orders that are not fully invoiced.
  - *Creează Comanda* (Create Order): performs the same search; if no order is
    found, creates a draft request for quotation for the message partner, with
    the reference as vendor reference, and links it.
- When the reference only belongs to an order that is already fully invoiced,
  *Find Order* does not link it again; the error names the order and its bills.
- A second click on a message already linked to the found order is blocked, so
  the document is not processed twice.
- When a PO is found or created, a note is posted in the PO chatter with a copy
  of the SPV XML attached (`ir.attachment` on `purchase.order`, deduplicated by
  checksum or by name and mimetype). When the vendor bill does not exist yet,
  the XML is taken from the ZIP archive downloaded from ANAF.
- The vendor bill created from the SPV message is linked to the PO lines
  (standard purchase matching), so the invoiced quantity is updated and the
  standard "Create Bill" does not produce a second bill. Bill lines that are not
  on the PO (transport, packaging) stay on the bill.
- With *Purchase UBL* (`deltatech_purchase_ubl`) installed, the bill lines are
  imported on the PO: directly, with a notification, when every line is matched
  by vendor code or barcode and the totals match; otherwise the import wizard
  opens in preview, so the user decides for each line (use a product, create a
  new product or ignore it). The vendor bill option is off when the SPV bill
  already exists.
- Non-blocking duplicate warnings in the chatter: a PO that already has another
  bill, "Create Bill" on a PO linked to an SPV bill, and a bill with the same
  deduplication key when the module providing that key is installed.

## How it works

1. Open an SPV message of type vendor bill.
2. Check `Purchase Reference` (auto-filled from the XML if present) or
   `Reference`, and `Partner`.
3. Use one of the header buttons:
   - *Find Order*: links the only match and continues with the import; if
     several orders match, opens the filtered list; if none, shows an error,
     naming the fully invoiced order when the reference belongs to one.
   - *Create Order*: searches first; if no order is found, creates a draft
     request for quotation for the message partner (the partner is required),
     links it and continues with the import; otherwise behaves like *Find Order*.

## Configuration

No special configuration is required. Ensure users have access rights to
Purchase Orders and attachments as per standard Odoo security rules.
Installing `deltatech_purchase_ubl` is recommended, so the order lines are
imported from the XML.

## Compatibility

- Odoo 20.0
- Depends on: `l10n_ro_message_spv`, `purchase`
