## 19.0.0.0.5 (2026-08-19)

- Add an integration test for ticket #9287 using a real (anonymized) SPV
  invoice XML, wrapped in a ZIP as downloaded from ANAF: verifies the
  purchase order created before the bill ends up with its lines imported by
  `deltatech_purchase_ubl`, and cross-checks the imported total against the
  order total using the same `_get_order_total_check` control key that
  `deltatech_purchase_ubl` already runs (confirmed manually on the Damira
  production order that triggered the ticket: order total 2749.37 RON
  matched the XML `PayableAmount` exactly).

## 19.0.0.0.4 (2026-08-19)

- Fix: purchase orders created from an SPV message before the vendor bill
  existed (`action_create_purchase`/`action_find_purchase`) ended up with no
  order lines, because the XML attachment used to trigger the automatic UBL
  import (`deltatech_purchase_ubl`) is derived from the bill's attachments
  (`attachment_xml_id`, which needs `invoice_id`) and was always empty in this
  case. `_clone_xml_attachment_for_purchase` now falls back to extracting the
  XML directly from the raw ANAF ZIP (`_get_xml_bytes`) when no bill exists
  yet, so the purchase order lines get imported as expected (ticket #9287).

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
