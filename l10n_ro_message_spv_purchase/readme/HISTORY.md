## 19.0.0.0.3 (2026-07-24)

- Hide/block the "Find Purchase Order" and "Create Purchase Order" buttons for
  SPV messages that are not purchase invoices/receipts (`message_type` in
  `in_invoice`/`in_receipt`), so they no longer show up on sales invoice/receipt
  SPV messages (ticket #9055).

## 19.0.0.0.2 (2026-07-23)

- Block reprocessing of an SPV message already linked to a purchase order:
  a second click on "Find Purchase Order"/"Create Purchase Order" used to
  re-attach the XML and trigger the automatic import from
  `deltatech_purchase_ubl`, which could create duplicate products, lines,
  receipts and vendor bills (ticket #9055). Now raises a `UserError` instead
  of reprocessing the document.

## 19.0.0.0.1

- Initial version: link SPV messages to purchase orders by order reference,
  find/create purchase orders from SPV messages, attach the SPV XML copy on
  the purchase order chatter.
