## 18.0.0.0.3 (2026-08-20)

- Fix: `_purchase_search_domain_from_ref` matched purchase orders by reference
  alone, so a generic/reused vendor reference (ticket #9290, Ridacon: 6 SPV
  bills over 6 months all reusing the reference "ZILNIC") kept linking new
  bills to the same, already fully-invoiced order. The domain now excludes
  orders with `invoice_status == 'invoiced'`, so a reused reference on an
  order that still has open invoicing keeps matching (partial invoicing is
  unaffected), but once an order is fully invoiced a new bill with the same
  reference falls through to creating a new order instead of piling onto a
  closed one. Ported from 19.0 (PR #514).

## 18.0.0.0.2 (2026-07-03)

- Fix `TypeError` on SPV download: adapt the `process_xml()` override to the
  new signature from `l10n_ro_message_spv` 18.0.2.1.0 (the `attachment_xml`
  argument was removed by the ZIP-only storage refactor).
- Attach the SPV XML on the purchase order even when the message is not yet
  linked to an invoice: since `attachment_xml_id` became a computed field
  (populated only after the invoice import), the XML is now derived on the
  fly from the stored signed ZIP via `_get_xml_bytes()`.

## 18.0.0.0.1

- Initial version: link SPV messages to purchase orders by order reference,
  find/create purchase orders from SPV messages, attach the SPV XML copy on
  the purchase order chatter.
