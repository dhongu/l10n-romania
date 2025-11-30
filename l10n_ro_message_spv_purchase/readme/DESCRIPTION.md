# Purchase Message SPV (Romania)

This addon extends the Romanian SPV message model (`l10n.ro.message.spv`) to help
procure-to-pay flows by linking SPV messages with Purchase Orders (PO) and
keeping the PO’s chatter and attachments in sync.

## Key features

- New fields on SPV message:
  - `Purchase Reference` (`purchase_ref`) – extracted automatically from XML
    at `OrderReference/ID` when available.
  - `Purchase Order` (`purchase_order_id`) – the linked PO, if any.
- Two dedicated actions on the SPV form:
  - Find Purchase: searches purchase orders by reference (using
    `purchase_ref` or fallback to `ref`) across `partner_ref`, `origin`, or
    `name`, narrowed by partner/company when available.
  - Create Purchase: performs the same search; if none is found and a partner
    is set, creates a draft PO and links it.
- When a PO is found or created, a note is posted to the PO’s chatter with a
  contextual message and the SPV XML attached.
- The SPV XML is not just referenced; a copy of the XML attachment is created
  on the PO (`ir.attachment` with `res_model='purchase.order'`), avoiding
  cross‑linking to the original message file.
- Duplicate prevention for attachments on the PO, based on checksum (with
  fallback to name and mimetype).

## How it works

1. Open an SPV message and ensure `Partner` is set.
2. Check `Purchase Reference` (auto‑filled from XML if present) or `Reference`.
3. Use one of the header buttons:
   - Find Purchase: links and opens the only match; if multiple matches are
     found, opens the filtered list; if none, shows a friendly error.
   - Create Purchase: searches first; if none is found, it creates a draft PO
     for the selected partner, links it and opens it; otherwise behaves like
     Find.
4. After linking/creating, the module posts a note on the PO and attaches a
   cloned copy of the SPV XML to the PO record.

## Configuration

No special configuration is required. Ensure users have access rights to
Purchase Orders and attachments as per standard Odoo security rules.

## Compatibility

- Odoo 17.0
- Depends on: `l10n_ro_message_spv`, `purchase`

## Notes

- If the SPV message has no XML attachment, only the note is posted to the PO.
- The attachment cloning uses `sudo()` to reliably create the copy on the PO.
- The search domain is deliberately constrained by partner and company when
  present to reduce false positives.
