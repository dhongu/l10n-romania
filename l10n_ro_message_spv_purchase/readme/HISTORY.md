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
