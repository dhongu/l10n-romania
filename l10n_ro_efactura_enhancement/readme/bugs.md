# Known bugs

Review date: 2026-10-10. Target version: Odoo 19.

## EFACTURA-001 — P2: Credit notes are sent without the reference of the corrected invoice (BT-25)

- **Status:** Open; found 2026-10-09 by the accounting review of AGREEMENT-009.
- **Location:** UBL/CIUS-RO export (`account_edi_ubl_cii._ubl_add_billing_reference_nodes` returns an empty list in Odoo 19; this module only applies length limits to `cac:BillingReference`).
- **Trigger:** Exporting a credit note (type 381) or a corrective invoice to e-Factura.
- **Actual behavior / impact:** `reversed_entry_id` (or the corrected invoices in `ref`) is not written as `cac:BillingReference/cac:InvoiceDocumentReference` (BT-25/BT-26). Art. 330(1)(b) and Art. 319(20)(r) Fiscal Code require the number and date of the corrected invoice on the corrective document; the buyer cannot match the credit note to the invoice in SPV. `l10n_ro_efactura_xml_rules` can add the node only by partner configuration.
- **Suggested fix:** Emit `cac:BillingReference` from `reversed_entry_id` (number + issue date) in the CIUS-RO builder; check in the CIUS-RO specification whether BT-25 is mandatory for type 381.
